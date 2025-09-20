import pandas as pd

# Replace 'your_file.xml' with the path to your XML file
xml_file = r'C:\Users\conta\Documents\GitHub\ChallengePremiersoft\pacientes.xml'

# Read the XML file into a DataFrame
df = pd.read_xml(xml_file)

# Display the DataFrame
print(df)