import douki

@douki
def kinetic_energy(mass: float, velocity: float) -> float:
    """
    title: Calculate kinetic energy
    summary: |
        Uses the classical formula KE = 0.5 * m * v².
    parameters:
        mass: mass of the object (kg)
        velocity: velocity of the object (m/s)
    returns: kinetic energy in joules
    examples: |
        >>> kinetic_energy(2, 3)
        9.0
    """
    return 0.5 * mass * velocity**2
help(kinetic_energy)