import pandas as pd


# Create a dictionary with dummy data
data = {
    'Column1': [1, 2, 3, 4, 5],
    'Column2': ['A', 'B', 'C', 'D', 'E'],
    'Column3': [True, False, True, False, True]
}

# Create a DataFrame from the dictionary
df = pd.DataFrame(data)

# Create a dictionary with dummy data
data2 = {
    'Name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
    'Age': [25, 32, 41, 28, 36],
    'City': ['New York', 'London', 'Paris', 'Tokyo', 'Sydney'],
    'Salary': [50000, 70000, 60000, 80000, 55000]
}

# Create a DataFrame from the dictionary
df2 = pd.DataFrame(data2)


file_path = f"gpt-3.5-turbo-2023-07-11_10-35-18874199'.xlsx"
with pd.ExcelWriter(path=file_path) as writer:
    df.to_excel(writer, sheet_name='first_dummy')
    df2.to_excel(writer, sheet_name='second_dummy')
