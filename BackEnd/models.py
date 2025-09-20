from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, Table, Float
from sqlalchemy.orm import relationship
from database import Base
import uuid

# Tabelas de associação (N:M)

medicos_hospitais = Table(
    'medicos_hospitais',
    Base.metadata,
    Column('medico_codigo', String(36), ForeignKey('medicos.codigo'), primary_key=True),
    Column('hospital_codigo', String(36), ForeignKey('hospitais.codigo'), primary_key=True)
)

hospitais_especialidades = Table(
    'hospitais_especialidades',
    Base.metadata,
    Column('hospital_codigo', String(36), ForeignKey('hospitais.codigo'), primary_key=True),
    Column('especialidade_id', Integer, ForeignKey('especialidades.id'), primary_key=True)
)

pacientes_hospitais = Table(
    'pacientes_hospitais',
    Base.metadata,
    Column('paciente_codigo', String(36), ForeignKey('pacientes.codigo'), primary_key=True),
    Column('hospital_codigo', String(36), ForeignKey('hospitais.codigo'), primary_key=True)
)

# Tabelas principais

class Estado(Base):
    __tablename__ = 'estados'

    codigo_uf = Column(Integer, primary_key=True)
    uf = Column(String(2), nullable=False, unique=True)
    nome = Column(String(100), nullable=False)
    latitude = Column(Float)
    longitude = Column(Float)
    regiao = Column(String(20), nullable=False)

    municipios = relationship("Municipio", back_populates="estado")


class Municipio(Base):
    __tablename__ = 'municipios'

    codigo_ibge = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    latitude = Column(Float)
    longitude = Column(Float)
    capital = Column(Boolean, default=False)
    codigo_uf = Column(Integer, ForeignKey('estados.codigo_uf'))
    siafi_id = Column(Integer)
    ddd = Column(String(5))
    fuso_horario = Column(String(50))
    populacao = Column(Integer)

    estado = relationship("Estado", back_populates="municipios")
    pacientes = relationship("Paciente", back_populates="municipio")
    hospitais = relationship("Hospital", back_populates="municipio")
    medicos = relationship("Medico", back_populates="municipio")


class Especialidade(Base):
    __tablename__ = 'especialidades'

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(100), unique=True, nullable=False)

    medicos = relationship("Medico", back_populates="especialidade")
    hospitais = relationship("Hospital", secondary=hospitais_especialidades, back_populates="especialidades")


class Hospital(Base):
    __tablename__ = 'hospitais'

    codigo = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nome = Column(String(100), nullable=False)
    municipio_id = Column(Integer, ForeignKey('municipios.codigo_ibge'))
    bairro = Column(String(100))
    leitos_totais = Column(Integer)

    municipio = relationship("Municipio", back_populates="hospitais")
    especialidades = relationship("Especialidade", secondary=hospitais_especialidades, back_populates="hospitais")
    medicos = relationship("Medico", secondary=medicos_hospitais, back_populates="hospitais")
    pacientes = relationship("Paciente", secondary=pacientes_hospitais, back_populates="hospitais")


class Medico(Base):
    __tablename__ = 'medicos'

    codigo = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nome_completo = Column(String(100), nullable=False)
    especialidade_id = Column(Integer, ForeignKey('especialidades.id'))
    municipio_id = Column(Integer, ForeignKey('municipios.codigo_ibge'))

    especialidade = relationship("Especialidade", back_populates="medicos")
    municipio = relationship("Municipio", back_populates="medicos")
    hospitais = relationship("Hospital", secondary=medicos_hospitais, back_populates="medicos")


class Cid10(Base):
    __tablename__ = 'cid10'

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(10), nullable=False)
    categoria = Column(String(255), nullable=False)
    descricao = Column(String(255), nullable=False)

    pacientes = relationship("Paciente", back_populates="cid10")


class Paciente(Base):
    __tablename__ = 'pacientes'

    codigo = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    cpf = Column(String(11), nullable=False, unique=True, index=True)
    nome_completo = Column(String(100), nullable=False)
    genero = Column(String(1))
    municipio_id = Column(Integer, ForeignKey('municipios.codigo_ibge'))
    bairro = Column(String(100))
    convenio = Column(String(3))
    cid10_id = Column(Integer, ForeignKey('cid10.id'))

    municipio = relationship("Municipio", back_populates="pacientes")
    cid10 = relationship("Cid10", back_populates="pacientes")
    hospitais = relationship("Hospital", secondary=pacientes_hospitais, back_populates="pacientes")
