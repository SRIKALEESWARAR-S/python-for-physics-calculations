# ============================================================
# 2003 CRICKET WORLD CUP
# LEGENDRE + RNN + TRANSFORMER RESEARCH BENCHMARK
#
# Models:
#   1. Majority baseline
#   2. GRU
#   3. LSTM
#   4. Transformer
#   5. Legendre Transformer
#
# Target:
#   0 = dot ball
#   1 = 1 run
#   2 = 2 runs
#   3 = 3 runs
#   4 = 4 runs
#   5 = 5+ runs
#   6 = wicket
#
# Input:
#   Previous WINDOW deliveries
# ============================================================

import os
import time
import copy
import random
import warnings

import numpy as np
import pandas as pd

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader

from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    f1_score,
    log_loss,
    confusion_matrix
)

from scipy.special import eval_legendre

warnings.filterwarnings("ignore")

# ============================================================
# 0. REPRODUCIBILITY
# ============================================================

SEED = 42

random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)

if torch.cuda.is_available():
    torch.cuda.manual_seed_all(SEED)

DEVICE = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

print("=" * 75)
print("LEGENDRE + RNN + TRANSFORMER CRICKET RESEARCH")
print("=" * 75)

print("\nDevice:", DEVICE)

# ============================================================
# 1. CONFIGURATION
# ============================================================

DATA_DIR = "/content/world_cup_2003_research_dataset"

DELIVERY_FILE = os.path.join(
    DATA_DIR,
    "deliveries_2003.csv"
)

RESULT_DIR = "/content/legendreq_2003_ml_results"

os.makedirs(
    RESULT_DIR,
    exist_ok=True
)

# Sequence length
WINDOW = 16

# Legendre polynomial order
LEGENDRE_ORDER = 5

# Neural network
HIDDEN = 64
N_LAYERS = 2
N_HEADS = 4
DROPOUT = 0.10

# Training
BATCH_SIZE = 64
EPOCHS = 15
LR = 1e-3
WEIGHT_DECAY = 1e-4

# Maximum training samples.
# Set to None to use everything.
MAX_TRAIN_SAMPLES = None

N_CLASSES = 7

print("\nConfiguration")
print("-------------------------")
print("Window:", WINDOW)
print("Legendre order:", LEGENDRE_ORDER)
print("Hidden:", HIDDEN)
print("Layers:", N_LAYERS)
print("Heads:", N_HEADS)
print("Epochs:", EPOCHS)
print("Batch size:", BATCH_SIZE)

# ============================================================
# 2. LOAD DATA
# ============================================================

if not os.path.exists(DELIVERY_FILE):
    raise FileNotFoundError(
        f"\nCould not find:\n{DELIVERY_FILE}\n\n"
        "Run the dataset-builder cell first."
    )

df = pd.read_csv(
    DELIVERY_FILE
)

print("\nRaw dataset shape:", df.shape)

print("\nColumns:")
print(df.columns.tolist())

# ============================================================
# 3. SORT DATA PROPERLY
# ============================================================

df["date"] = pd.to_datetime(
    df["date"],
    errors="coerce"
)

df = df.sort_values(
    [
        "date",
        "match_id",
        "innings",
        "over",
        "ball_in_over"
    ]
).reset_index(drop=True)

# ============================================================
# 4. DERIVE FEATURES
#
# This is where the previous error occurred.
#
# We explicitly CREATE:
#   over_index0
#   ball_index_in_over
#   cumulative_runs
#   cumulative_wickets
# ============================================================

# Zero-based over
df["over_index0"] = (
    pd.to_numeric(
        df["over"],
        errors="coerce"
    ).fillna(1).astype(float) - 1.0
)

# Ball position within over
df["ball_index_in_over"] = (
    pd.to_numeric(
        df["ball_in_over"],
        errors="coerce"
    ).fillna(1).astype(float) - 1.0
)

# Runs before target delivery.
#
# IMPORTANT:
# The current row is the target ball.
# Therefore subtract the current ball's runs.
df["cumulative_runs"] = (
    pd.to_numeric(
        df["innings_cumulative_runs"],
        errors="coerce"
    ).fillna(0)
    - pd.to_numeric(
        df["total_runs"],
        errors="coerce"
    ).fillna(0)
)

# Wickets before target delivery
df["cumulative_wickets"] = (
    pd.to_numeric(
        df["innings_cumulative_wickets"],
        errors="coerce"
    ).fillna(0)
    - pd.to_numeric(
        df["is_wicket"],
        errors="coerce"
    ).fillna(0)
)

# ============================================================
# 5. NUMERIC CLEANING
# ============================================================

numeric_columns = [
    "total_runs",
    "batter_runs",
    "extras_runs",
    "is_wicket",
    "over_index0",
    "ball_index_in_over",
    "cumulative_runs",
    "cumulative_wickets",
    "legal_balls_elapsed"
]

for col in numeric_columns:

    df[col] = pd.to_numeric(
        df[col],
        errors="coerce"
    ).fillna(0)

# ============================================================
# 6. TARGET
#
# 0 = dot
# 1 = 1 run
# ...
# 4 = 4 runs
# 5 = 5+ runs
# 6 = wicket
# ============================================================

def make_target(row):

    if row["is_wicket"] == 1:
        return 6

    runs = int(row["total_runs"])

    if runs >= 5:
        return 5

    return runs


df["target"] = df.apply(
    make_target,
    axis=1
)

print("\nTarget distribution:")

target_counts = (
    df["target"]
    .value_counts()
    .sort_index()
)

print(target_counts)

# ============================================================
# 7. FEATURES
# ============================================================

FEATURES = [
    "total_runs",
    "batter_runs",
    "extras_runs",
    "is_wicket",
    "over_index0",
    "ball_index_in_over",
    "cumulative_runs",
    "cumulative_wickets",
    "legal_balls_elapsed"
]

print("\nFeatures:")
for f in FEATURES:
    print("  ", f)

X_all = df[FEATURES].values.astype(
    np.float32
)

y_all = df["target"].values.astype(
    np.int64
)

# ============================================================
# 8. MATCH-LEVEL CHRONOLOGICAL SPLIT
#
# NO RANDOM DELIVERY SPLIT.
#
# This prevents deliveries from the same match appearing
# in both train and test.
# ============================================================

match_table = (
    df[
        [
            "match_id",
            "date"
        ]
    ]
    .drop_duplicates()
    .sort_values(
        [
            "date",
            "match_id"
        ]
    )
    .reset_index(drop=True)
)

n_matches = len(match_table)

train_end = int(
    0.70 * n_matches
)

val_end = int(
    0.85 * n_matches
)

train_matches = set(
    match_table.iloc[
        :train_end
    ]["match_id"]
)

val_matches = set(
    match_table.iloc[
        train_end:val_end
    ]["match_id"]
)

test_matches = set(
    match_table.iloc[
        val_end:
    ]["match_id"]
)

print("\nChronological split")
print("-------------------------")
print("Total matches:", n_matches)
print("Train matches:", len(train_matches))
print("Validation matches:", len(val_matches))
print("Test matches:", len(test_matches))

print("\nTrain:")
print(sorted(train_matches))

print("\nValidation:")
print(sorted(val_matches))

print("\nTest:")
print(sorted(test_matches))

# ============================================================
# 9. TRAIN-ONLY NORMALIZATION
# ============================================================

train_mask = df["match_id"].isin(
    train_matches
)

feature_mean = (
    df.loc[
        train_mask,
        FEATURES
    ]
    .mean()
    .values
    .astype(np.float32)
)

feature_std = (
    df.loc[
        train_mask,
        FEATURES
    ]
    .std()
    .values
    .astype(np.float32)
)

feature_std[
    feature_std < 1e-6
] = 1.0

X_normalized = (
    X_all - feature_mean
) / feature_std

# ============================================================
# 10. BUILD SEQUENTIAL WINDOWS
#
# Each sample:
#
# X[t-WINDOW : t]
#          |
#          +--> predict delivery t
#
# Windows NEVER cross innings.
# ============================================================

def build_windows(
    data,
    normalized_X,
    match_ids
):

    samples = []
    labels = []

    selected_matches = set(match_ids)

    grouped = data.groupby(
        [
            "match_id",
            "innings"
        ],
        sort=False
    )

    for (
        (match_id, innings),
        group
    ) in grouped:

        if match_id not in selected_matches:
            continue

        indices = group.index.to_numpy()

        # Need at least WINDOW + 1 deliveries
        if len(indices) <= WINDOW:
            continue

        for i in range(
            WINDOW,
            len(indices)
        ):

            window_indices = indices[
                i-WINDOW:i
            ]

            target_index = indices[i]

            samples.append(
                normalized_X[
                    window_indices
                ]
            )

            labels.append(
                int(
                    data.loc[
                        target_index,
                        "target"
                    ]
                )
            )

    if len(samples) == 0:
        return (
            np.empty(
                (
                    0,
                    WINDOW,
                    len(FEATURES)
                ),
                dtype=np.float32
            ),
            np.empty(
                (0,),
                dtype=np.int64
            )
        )

    return (
        np.asarray(
            samples,
            dtype=np.float32
        ),
        np.asarray(
            labels,
            dtype=np.int64
        )
    )

# ============================================================
# 11. CREATE DATASETS
# ============================================================

X_train, y_train = build_windows(
    df,
    X_normalized,
    train_matches
)

X_val, y_val = build_windows(
    df,
    X_normalized,
    val_matches
)

X_test, y_test = build_windows(
    df,
    X_normalized,
    test_matches
)

print("\nWindowed datasets")
print("-------------------------")

print(
    "Train:",
    X_train.shape,
    y_train.shape
)

print(
    "Validation:",
    X_val.shape,
    y_val.shape
)

print(
    "Test:",
    X_test.shape,
    y_test.shape
)

if len(X_train) == 0:
    raise RuntimeError(
        "Training set contains no windows."
    )

if len(X_test) == 0:
    raise RuntimeError(
        "Test set contains no windows."
    )

# ============================================================
# 12. OPTIONAL TRAIN SAMPLE LIMIT
# ============================================================

if (
    MAX_TRAIN_SAMPLES is not None
    and len(X_train) > MAX_TRAIN_SAMPLES
):

    rng = np.random.default_rng(
        SEED
    )

    idx = rng.choice(
        len(X_train),
        size=MAX_TRAIN_SAMPLES,
        replace=False
    )

    X_train = X_train[idx]
    y_train = y_train[idx]

    print(
        "\nTraining samples limited to:",
        MAX_TRAIN_SAMPLES
    )

# ============================================================
# 13. PYTORCH DATASET
# ============================================================

class CricketDataset(
    Dataset
):

    def __init__(
        self,
        X,
        y
    ):

        self.X = torch.tensor(
            X,
            dtype=torch.float32
        )

        self.y = torch.tensor(
            y,
            dtype=torch.long
        )

    def __len__(self):
        return len(self.y)

    def __getitem__(
        self,
        idx
    ):

        return (
            self.X[idx],
            self.y[idx]
        )


train_dataset = CricketDataset(
    X_train,
    y_train
)

val_dataset = CricketDataset(
    X_val,
    y_val
)

test_dataset = CricketDataset(
    X_test,
    y_test
)

train_loader = DataLoader(
    train_dataset,
    batch_size=BATCH_SIZE,
    shuffle=True,
    num_workers=0,
    pin_memory=torch.cuda.is_available()
)

val_loader = DataLoader(
    val_dataset,
    batch_size=BATCH_SIZE,
    shuffle=False,
    num_workers=0,
    pin_memory=torch.cuda.is_available()
)

test_loader = DataLoader(
    test_dataset,
    batch_size=BATCH_SIZE,
    shuffle=False,
    num_workers=0,
    pin_memory=torch.cuda.is_available()
)

INPUT_DIM = len(FEATURES)

# ============================================================
# 14. GRU MODEL
# ============================================================

class GRUModel(nn.Module):

    def __init__(
        self,
        input_dim,
        hidden,
        layers,
        classes,
        dropout
    ):

        super().__init__()

        self.rnn = nn.GRU(
            input_size=input_dim,
            hidden_size=hidden,
            num_layers=layers,
            batch_first=True,
            dropout=(
                dropout
                if layers > 1
                else 0
            )
        )

        self.head = nn.Sequential(
            nn.Linear(
                hidden,
                hidden
            ),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(
                hidden,
                classes
            )
        )

    def forward(self, x):

        out, _ = self.rnn(x)

        return self.head(
            out[:, -1, :]
        )

# ============================================================
# 15. LSTM MODEL
# ============================================================

class LSTMModel(nn.Module):

    def __init__(
        self,
        input_dim,
        hidden,
        layers,
        classes,
        dropout
    ):

        super().__init__()

        self.rnn = nn.LSTM(
            input_size=input_dim,
            hidden_size=hidden,
            num_layers=layers,
            batch_first=True,
            dropout=(
                dropout
                if layers > 1
                else 0
            )
        )

        self.head = nn.Sequential(
            nn.Linear(
                hidden,
                hidden
            ),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(
                hidden,
                classes
            )
        )

    def forward(self, x):

        out, _ = self.rnn(x)

        return self.head(
            out[:, -1, :]
        )

# ============================================================
# 16. TRANSFORMER POSITIONAL ENCODING
# ============================================================

class PositionalEncoding(
    nn.Module
):

    def __init__(
        self,
        d_model,
        max_len=512
    ):

        super().__init__()

        position = torch.arange(
            max_len
        ).unsqueeze(1).float()

        div_term = torch.exp(
            torch.arange(
                0,
                d_model,
                2
            ).float()
            * (
                -np.log(10000.0)
                / d_model
            )
        )

        pe = torch.zeros(
            max_len,
            d_model
        )

        pe[:, 0::2] = torch.sin(
            position * div_term
        )

        pe[:, 1::2] = torch.cos(
            position * div_term
        )

        pe = pe.unsqueeze(0)

        self.register_buffer(
            "pe",
            pe
        )

    def forward(self, x):

        return x + self.pe[
            :, :x.size(1)
        ]

# ============================================================
# 17. TRANSFORMER MODEL
# ============================================================

class TransformerModel(
    nn.Module
):

    def __init__(
        self,
        input_dim,
        hidden,
        heads,
        layers,
        classes,
        dropout
    ):

        super().__init__()

        self.embedding = nn.Linear(
            input_dim,
            hidden
        )

        self.position = (
            PositionalEncoding(
                hidden,
                WINDOW
            )
        )

        encoder_layer = (
            nn.TransformerEncoderLayer(
                d_model=hidden,
                nhead=heads,
                dim_feedforward=hidden * 2,
                dropout=dropout,
                batch_first=True,
                activation="gelu"
            )
        )

        self.encoder = (
            nn.TransformerEncoder(
                encoder_layer,
                num_layers=layers
            )
        )

        self.head = nn.Sequential(
            nn.Linear(
                hidden,
                hidden
            ),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(
                hidden,
                classes
            )
        )

    def forward(self, x):

        x = self.embedding(x)

        x = self.position(x)

        x = self.encoder(x)

        return self.head(
            x[:, -1, :]
        )

# ============================================================
# 18. LEGENDRE TRANSFORM
# ============================================================

def legendre_transform(
    X,
    order
):

    """
    X shape:
        [samples, time, features]

    Returns:
        [samples, order+1, features]
    """

    n_samples = X.shape[0]
    n_time = X.shape[1]
    n_features = X.shape[2]

    # Time coordinate
    t = np.linspace(
        -1.0,
        1.0,
        n_time
    )

    # Legendre basis
    basis = np.stack(
        [
            eval_legendre(
                k,
                t
            )
            for k in range(
                order + 1
            )
        ],
        axis=1
    )

    # Pseudoinverse
    pinv = np.linalg.pinv(
        basis
    )

    # Flatten samples
    flat = X.reshape(
        n_samples,
        n_time,
        n_features
    )

    # Project
    transformed = np.einsum(
        "kt,ntf->nkf",
        pinv,
        flat
    )

    return transformed.astype(
        np.float32
    )

# ============================================================
# 19. CREATE LEGENDRE DATA
# ============================================================

print("\nCalculating Legendre representation...")

X_train_leg = legendre_transform(
    X_train,
    LEGENDRE_ORDER
)

X_val_leg = legendre_transform(
    X_val,
    LEGENDRE_ORDER
)

X_test_leg = legendre_transform(
    X_test,
    LEGENDRE_ORDER
)

print(
    "Legendre train shape:",
    X_train_leg.shape
)

print(
    "Legendre validation shape:",
    X_val_leg.shape
)

print(
    "Legendre test shape:",
    X_test_leg.shape
)

# ============================================================
# 20. LEGENDRE DATA LOADERS
# ============================================================

train_leg_dataset = CricketDataset(
    X_train_leg,
    y_train
)

val_leg_dataset = CricketDataset(
    X_val_leg,
    y_val
)

test_leg_dataset = CricketDataset(
    X_test_leg,
    y_test
)

train_leg_loader = DataLoader(
    train_leg_dataset,
    batch_size=BATCH_SIZE,
    shuffle=True,
    num_workers=0,
    pin_memory=torch.cuda.is_available()
)

val_leg_loader = DataLoader(
    val_leg_dataset,
    batch_size=BATCH_SIZE,
    shuffle=False,
    num_workers=0,
    pin_memory=torch.cuda.is_available()
)

test_leg_loader = DataLoader(
    test_leg_dataset,
    batch_size=BATCH_SIZE,
    shuffle=False,
    num_workers=0,
    pin_memory=torch.cuda.is_available()
)

# ============================================================
# 21. LEGENDRE TRANSFORMER
# ============================================================

LEGENDRE_INPUT_DIM = (
    LEGENDRE_ORDER + 1
)

# Each Legendre coefficient is treated as a time/token.
# Features are flattened into the token embedding.

class LegendreTransformer(
    nn.Module
):

    def __init__(
        self,
        n_features,
        order,
        hidden,
        heads,
        layers,
        classes,
        dropout
    ):

        super().__init__()

        self.input_dim = (
            n_features
        )

        self.embedding = nn.Linear(
            n_features,
            hidden
        )

        self.position = (
            PositionalEncoding(
                hidden,
                order + 1
            )
        )

        encoder_layer = (
            nn.TransformerEncoderLayer(
                d_model=hidden,
                nhead=heads,
                dim_feedforward=hidden * 2,
                dropout=dropout,
                batch_first=True,
                activation="gelu"
            )
        )

        self.encoder = (
            nn.TransformerEncoder(
                encoder_layer,
                num_layers=layers
            )
        )

        self.head = nn.Sequential(
            nn.Linear(
                hidden,
                hidden
            ),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(
                hidden,
                classes
            )
        )

    def forward(self, x):

        x = self.embedding(x)

        x = self.position(x)

        x = self.encoder(x)

        return self.head(
            x[:, -1, :]
        )

# ============================================================
# 22. MODEL FACTORY
# ============================================================

def create_model(
    name
):

    if name == "GRU":

        return GRUModel(
            INPUT_DIM,
            HIDDEN,
            N_LAYERS,
            N_CLASSES,
            DROPOUT
        ).to(DEVICE)

    elif name == "LSTM":

        return LSTMModel(
            INPUT_DIM,
            HIDDEN,
            N_LAYERS,
            N_CLASSES,
            DROPOUT
        ).to(DEVICE)

    elif name == "Transformer":

        return TransformerModel(
            INPUT_DIM,
            HIDDEN,
            N_HEADS,
            N_LAYERS,
            N_CLASSES,
            DROPOUT
        ).to(DEVICE)

    elif name == "LegendreTransformer":

        return LegendreTransformer(
            INPUT_DIM,
            LEGENDRE_ORDER,
            HIDDEN,
            N_HEADS,
            N_LAYERS,
            N_CLASSES,
            DROPOUT
        ).to(DEVICE)

    else:

        raise ValueError(
            f"Unknown model: {name}"
        )

# ============================================================
# 23. TRAINING FUNCTION
# ============================================================

def train_model(
    model,
    train_loader,
    val_loader,
    epochs=EPOCHS
):

    criterion = nn.CrossEntropyLoss()

    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=LR,
        weight_decay=WEIGHT_DECAY
    )

    best_val_loss = np.inf
    best_state = None

    history = []

    for epoch in range(
        1,
        epochs + 1
    ):

        # -------------------------
        # TRAIN
        # -------------------------

        model.train()

        train_loss = 0.0
        train_count = 0

        for X, y in train_loader:

            X = X.to(
                DEVICE,
                non_blocking=True
            )

            y = y.to(
                DEVICE,
                non_blocking=True
            )

            optimizer.zero_grad(
                set_to_none=True
            )

            logits = model(X)

            loss = criterion(
                logits,
                y
            )

            loss.backward()

            torch.nn.utils.clip_grad_norm_(
                model.parameters(),
                max_norm=1.0
            )

            optimizer.step()

            train_loss += (
                loss.item()
                * len(y)
            )

            train_count += len(y)

        train_loss /= max(
            train_count,
            1
        )

        # -------------------------
        # VALIDATION
        # -------------------------

        model.eval()

        val_loss = 0.0
        val_count = 0

        with torch.no_grad():

            for X, y in val_loader:

                X = X.to(
                    DEVICE,
                    non_blocking=True
                )

                y = y.to(
                    DEVICE,
                    non_blocking=True
                )

                logits = model(X)

                loss = criterion(
                    logits,
                    y
                )

                val_loss += (
                    loss.item()
                    * len(y)
                )

                val_count += len(y)

        val_loss /= max(
            val_count,
            1
        )

        history.append({
            "epoch": epoch,
            "train_loss": train_loss,
            "val_loss": val_loss
        })

        if val_loss < best_val_loss:

            best_val_loss = val_loss

            best_state = copy.deepcopy(
                model.state_dict()
            )

        print(
            f"Epoch {epoch:02d}/{epochs} "
            f"| train={train_loss:.4f} "
            f"| val={val_loss:.4f}"
        )

    if best_state is not None:

        model.load_state_dict(
            best_state
        )

    return (
        model,
        pd.DataFrame(history)
    )

# ============================================================
# 24. EVALUATION
# ============================================================

def evaluate_model(
    model,
    loader,
    y_true
):

    model.eval()

    all_probabilities = []

    start = time.perf_counter()

    with torch.no_grad():

        for X, y in loader:

            X = X.to(
                DEVICE,
                non_blocking=True
            )

            logits = model(X)

            probabilities = torch.softmax(
                logits,
                dim=1
            )

            all_probabilities.append(
                probabilities.cpu().numpy()
            )

    if DEVICE.type == "cuda":
        torch.cuda.synchronize()

    elapsed = (
        time.perf_counter()
        - start
    )

    probabilities = np.concatenate(
        all_probabilities,
        axis=0
    )

    predictions = np.argmax(
        probabilities,
        axis=1
    )

    accuracy = accuracy_score(
        y_true,
        predictions
    )

    balanced = balanced_accuracy_score(
        y_true,
        predictions
    )

    macro_f1 = f1_score(
        y_true,
        predictions,
        average="macro",
        zero_division=0
    )

    weighted_f1 = f1_score(
        y_true,
        predictions,
        average="weighted",
        zero_division=0
    )

    try:

        ll = log_loss(
            y_true,
            probabilities,
            labels=np.arange(
                N_CLASSES
            )
        )

    except Exception:

        ll = np.nan

    latency_ms = (
        elapsed
        / max(
            len(y_true),
            1
        )
        * 1000
    )

    return {
        "accuracy": accuracy,
        "balanced_accuracy": balanced,
        "macro_f1": macro_f1,
        "weighted_f1": weighted_f1,
        "log_loss": ll,
        "latency_ms_per_sample": latency_ms
    }, predictions, probabilities

# ============================================================
# 25. MAJORITY BASELINE
# ============================================================

majority_class = int(
    pd.Series(y_train)
    .value_counts()
    .idxmax()
)

majority_predictions = np.full(
    len(y_test),
    majority_class
)

majority_prob = np.zeros(
    (
        len(y_test),
        N_CLASSES
    ),
    dtype=np.float64
)

majority_prob[
    :,
    majority_class
] = 1.0

majority_result = {

    "accuracy": accuracy_score(
        y_test,
        majority_predictions
    ),

    "balanced_accuracy":
        balanced_accuracy_score(
            y_test,
            majority_predictions
        ),

    "macro_f1":
        f1_score(
            y_test,
            majority_predictions,
            average="macro",
            zero_division=0
        ),

    "weighted_f1":
        f1_score(
            y_test,
            majority_predictions,
            average="weighted",
            zero_division=0
        ),

    "log_loss":
        log_loss(
            y_test,
            majority_prob,
            labels=np.arange(
                N_CLASSES
            )
        ),

    "latency_ms_per_sample":
        0.0
}

results = []

results.append({
    "model": "Majority",
    **majority_result
})

# ============================================================
# 26. TRAIN GRU
# ============================================================

print("\n")
print("=" * 75)
print("TRAINING GRU")
print("=" * 75)

gru = create_model(
    "GRU"
)

gru, gru_history = train_model(
    gru,
    train_loader,
    val_loader
)

gru_metrics, gru_pred, gru_prob = evaluate_model(
    gru,
    test_loader,
    y_test
)

results.append({
    "model": "GRU",
    **gru_metrics
})

# ============================================================
# 27. TRAIN LSTM
# ============================================================

print("\n")
print("=" * 75)
print("TRAINING LSTM")
print("=" * 75)

lstm = create_model(
    "LSTM"
)

lstm, lstm_history = train_model(
    lstm,
    train_loader,
    val_loader
)

lstm_metrics, lstm_pred, lstm_prob = evaluate_model(
    lstm,
    test_loader,
    y_test
)

results.append({
    "model": "LSTM",
    **lstm_metrics
})

# ============================================================
# 28. TRAIN RAW TRANSFORMER
# ============================================================

print("\n")
print("=" * 75)
print("TRAINING RAW TRANSFORMER")
print("=" * 75)

transformer = create_model(
    "Transformer"
)

transformer, transformer_history = train_model(
    transformer,
    train_loader,
    val_loader
)

transformer_metrics, transformer_pred, transformer_prob = evaluate_model(
    transformer,
    test_loader,
    y_test
)

results.append({
    "model": "Transformer",
    **transformer_metrics
})

# ============================================================
# 29. TRAIN LEGENDRE TRANSFORMER
# ============================================================

print("\n")
print("=" * 75)
print("TRAINING LEGENDRE TRANSFORMER")
print("=" * 75)

legendre_model = create_model(
    "LegendreTransformer"
)

legendre_model, legendre_history = train_model(
    legendre_model,
    train_leg_loader,
    val_leg_loader
)

legendre_metrics, legendre_pred, legendre_prob = evaluate_model(
    legendre_model,
    test_leg_loader,
    y_test
)

results.append({
    "model": "LegendreTransformer",
    **legendre_metrics
})

# ============================================================
# 30. RESULTS TABLE
# ============================================================

results_df = pd.DataFrame(
    results
)

results_df = results_df.sort_values(
    "macro_f1",
    ascending=False
).reset_index(
    drop=True
)

print("\n")
print("=" * 75)
print("FINAL TEST BENCHMARK")
print("=" * 75)

display(
    results_df.style.format({
        "accuracy": "{:.4f}",
        "balanced_accuracy": "{:.4f}",
        "macro_f1": "{:.4f}",
        "weighted_f1": "{:.4f}",
        "log_loss": "{:.4f}",
        "latency_ms_per_sample": "{:.4f}"
    })
)

# ============================================================
# 31. CONFUSION MATRIX
# ============================================================

model_predictions = {
    "GRU": gru_pred,
    "LSTM": lstm_pred,
    "Transformer": transformer_pred,
    "LegendreTransformer": legendre_pred
}

for name, pred in model_predictions.items():

    cm = confusion_matrix(
        y_test,
        pred,
        labels=np.arange(
            N_CLASSES
        )
    )

    cm_df = pd.DataFrame(
        cm,
        index=[
            "0_dot",
            "1_run",
            "2_runs",
            "3_runs",
            "4_runs",
            "5plus",
            "wicket"
        ],
        columns=[
            "0_dot",
            "1_run",
            "2_runs",
            "3_runs",
            "4_runs",
            "5plus",
            "wicket"
        ]
    )

    cm_path = os.path.join(
        RESULT_DIR,
        f"{name}_confusion_matrix.csv"
    )

    cm_df.to_csv(
        cm_path
    )

# ============================================================
# 32. SAVE PREDICTIONS
# ============================================================

predictions_df = pd.DataFrame({

    "y_true": y_test,

    "GRU_prediction":
        gru_pred,

    "LSTM_prediction":
        lstm_pred,

    "Transformer_prediction":
        transformer_pred,

    "LegendreTransformer_prediction":
        legendre_pred
})

prediction_path = os.path.join(
    RESULT_DIR,
    "test_predictions.csv"
)

predictions_df.to_csv(
    prediction_path,
    index=False
)

# ============================================================
# 33. SAVE BENCHMARK
# ============================================================

benchmark_path = os.path.join(
    RESULT_DIR,
    "model_benchmark.csv"
)

results_df.to_csv(
    benchmark_path,
    index=False
)

# ============================================================
# 34. SAVE TRAINING HISTORIES
# ============================================================

gru_history.to_csv(
    os.path.join(
        RESULT_DIR,
        "gru_history.csv"
    ),
    index=False
)

lstm_history.to_csv(
    os.path.join(
        RESULT_DIR,
        "lstm_history.csv"
    ),
    index=False
)

transformer_history.to_csv(
    os.path.join(
        RESULT_DIR,
        "transformer_history.csv"
    ),
    index=False
)

legendre_history.to_csv(
    os.path.join(
        RESULT_DIR,
        "legendre_transformer_history.csv"
    ),
    index=False
)

# ============================================================
# 35. SAVE NORMALIZATION PARAMETERS
# ============================================================

np.save(
    os.path.join(
        RESULT_DIR,
        "feature_mean.npy"
    ),
    feature_mean
)

np.save(
    os.path.join(
        RESULT_DIR,
        "feature_std.npy"
    ),
    feature_std
)

# ============================================================
# 36. RESEARCH SUMMARY
# ============================================================

print("\n")
print("=" * 75)
print("RESEARCH RUN COMPLETE")
print("=" * 75)

print(
    "\nDataset:",
    len(df),
    "deliveries"
)

print(
    "Matches:",
    n_matches
)

print(
    "Training windows:",
    len(X_train)
)

print(
    "Validation windows:",
    len(X_val)
)

print(
    "Test windows:",
    len(X_test)
)

print(
    "\nResults saved to:"
)

print(
    RESULT_DIR
)

print("\nBest model by macro-F1:")

best_model = results_df.iloc[0]

print(
    best_model["model"],
    "| Macro-F1 =",
    f"{best_model['macro_f1']:.4f}"
)

print("\nBenchmark file:")
print(benchmark_path)

print("\nPrediction file:")
print(prediction_path)

print("\n" + "=" * 75)
print("NEXT RESEARCH STAGE:")
print("Legendre Transformer + numerical RAG retrieval")
print("=" * 75)
