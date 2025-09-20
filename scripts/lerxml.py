import xml.etree.ElementTree as ET

def processa_paciente(paciente_elem):
    codigo = paciente_elem.find("Codigo").text
    cpf = paciente_elem.find("CPF").text
    nome = paciente_elem.find("Nome_Completo").text
    genero = paciente_elem.find("Genero").text
    cod_municipio = paciente_elem.find("Cod_municipio").text
    bairro = paciente_elem.find("Bairro").text
    convenio = paciente_elem.find("Convenio").text
    cid10 = paciente_elem.find("CID-10").text

    print(f"Paciente: {nome}, CPF: {cpf}, CID10: {cid10}")
    # Aqui você pode salvar, processar, inserir no banco, etc.

arquivo_xml = "pacientes.xml"

contexto = ET.iterparse(arquivo_xml, events=("end",))
for evento, elem in contexto:
    if elem.tag == "Paciente":
        processa_paciente(elem)
        elem.clear()  # libera memória para o próximo paciente
