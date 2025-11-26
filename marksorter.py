scores = [98, 56, 67, 67, 89, 45, 66, 89, 23, 45, 65, 90, 23, 101]
result = []

for score in scores:
    if score < 35:
        status = "fail"
    elif score > 100:
        status = "wrong input"
    else:
        status = "Pass"

    result.append({'score': score, 'status': status})

print(result)
