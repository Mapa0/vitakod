import psycopg2
from shapely.geometry import Point # Point class
from shapely.geometry import shape
import uuid
import shapefile
import json
from os import path
from rich import print

class GeographicOperations:
    def __init__(self):
        pass
    
    def get_point_geo_info(self, lat, long):
        return self.check_point_in_shapefile(["../shapefile/CampoGrande_Regioes_2021/Regioes_region.shp", "../shapefile/BR_UF_2021/BR_UF_2021.shp","../shapefile/MS_Municipios_2021/MS_Municipios_2021.shp"], lat, long)
    
    def check_point_in_shapefile(self, shp_paths, lat, long):
        dirname = path.dirname(path.abspath(__file__))
        point_to_check = (long, lat)
        regiao = None
        uf = None
        municipio = None
        cod_ibge = None
        for shp_idx, shp_path in enumerate(shp_paths):
            filename = path.join(dirname, shp_path)
            shp = shapefile.Reader(filename) 
            all_shapes = shp.shapes()
            all_records = shp.records()    
            for index, shp_shape in enumerate(all_shapes):
                if Point(point_to_check).within(shape(shp_shape)):
                    if shp_idx == 0:
                        regiao = all_records[index][0].lower()
                    elif shp_idx == 1:
                        uf = all_records[index][2]
                    elif shp_idx == 2:
                        cod_ibge = all_records[index][0]
                        municipio = all_records[index][1]
        return {
            "regiao": regiao,
            "uf": uf,
            "municipio": municipio,
            "cod_ibge": cod_ibge
        }

class DataCollector:
    def __init__(self):
        self.endpoint = "vitacaptis.ccqjibk2mgb8.us-east-1.rds.amazonaws.com"
        self.port = "5432"
        self.dbname = "postgres"
        self.user = "vitakod"
        self.password = "vita=kod22"
        self.geo_operations = GeographicOperations()
        self.conn = self.get_connection()

    def insert_report(self, sexo, faixa_etaria, uf, municipio, regiao_saude, user_id, cod_ibge, lat, long, report_id):
        try:
            cur = self.conn.cursor()
            cur.execute("INSERT INTO reports (sexo, faixa_etaria, uf, municipio, regiao_saude, user_id, cod_ibge, lat, long, report_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);",(sexo, faixa_etaria, uf, municipio, regiao_saude, user_id, cod_ibge, lat, long, report_id))
            self.conn.commit()
            return True
        except Exception as e:
            print(e)
            return False

    def insert_sintomas(self, sintomas, report_id):
        try:
            cur = self.conn.cursor()
            for sintoma in sintomas:
                cur.execute("INSERT INTO sintomas (report_id, tipo, descricao) VALUES (%s, %s, %s);",(report_id, sintoma["tipo"], sintoma["descricao"]))
            self.conn.commit()
            self.conn.close()
            return True
        except Exception as e:
            print(e)
            return False
        
    def get_connection(self):
        try:
            conn = psycopg2.connect(host=self.endpoint, port=self.port, database=self.dbname, user=self.user, password=self.password)
            #cur = conn.cursor()
            #cur.execute("""SELECT now()""")
            #query_results = cur.fetchall()
            #print(query_results)
            return conn
        except Exception as e:
            print("Database connection failed due to {}".format(e))
               
    def save_report(self, report):
        report_id = str(uuid.uuid4())
        sexo = report["sexo"]
        faixa_etaria = report["faixa_etaria"]
        lat = report["lat"]
        long = report["lng"]
        user_id = report["user_id"]
        geo = self.geo_operations.get_point_geo_info(float(lat), float(long))
        uf = geo['uf']
        municipio = geo['municipio']
        regiao_saude = geo['regiao']
        cod_ibge = geo['cod_ibge']
        sintomas = report['sintomas']
        if(self.insert_report(sexo, faixa_etaria, uf, municipio, regiao_saude, user_id, cod_ibge, lat, long, report_id)):
            if(self.insert_sintomas(sintomas, report_id)):
                #TODO gerenciamento de pontos e seguro -> VITACLUB
                return True
        return False