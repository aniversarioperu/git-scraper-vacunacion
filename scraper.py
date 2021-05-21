import pandas as pd
import pandasql as ps

URL_DATA='https://cloud.minsa.gob.pe/s/ZgXoXqK2KLjRLxD/download'
df=pd.read_csv(URL_DATA)


# Delete all not wanted columns
df.drop(['UUID', 'GRUPO_RIESGO', 'FABRICANTE', 'DIRESA', 'PROVINCIA', 'DISTRITO'], axis=1, inplace=True)

# Please write the full query on one line
# DOSIS 1 y 2
query_dosis="""select FECHA_CORTE, FECHA_VACUNACION, count (case when DOSIS = 1 then 1 end) as DOSIS1, count (case when DOSIS = 2 then 1 end) as DOSIS2 from df group by FECHA_VACUNACION """
result_query_dosis=ps.sqldf(query_dosis,locals())
print(ps.sqldf(query_dosis,locals()))

# Please write the full query on one line
# ACUMULADOS DOSIS 1 Y 2
query_acumulados="""select FECHA_CORTE, FECHA_VACUNACION, sum(count (case when DOSIS = 1 then 1 end)) over (order by FECHA_VACUNACION) as ACUMULADO1, sum(count (case when DOSIS = 2 then 1 end)) over (order by FECHA_VACUNACION) as ACUMULADO2 from df group by FECHA_VACUNACION"""
result_query_acumulados=ps.sqldf(query_acumulados,locals())
print(ps.sqldf(query_acumulados,locals()))

# Please write the full query on one line
# ACUMULADO DEPARTAMENTOS
query_departamentos="""select FECHA_CORTE, DEPARTAMENTO, count (case when DOSIS = 1 then 1 end) as DOSIS1, count (case when DOSIS = 2 then 1 end) as DOSIS2 from df group by DEPARTAMENTO"""
result_query_departamentos=ps.sqldf(query_departamentos,locals())
print(ps.sqldf(query_departamentos,locals()))

# Please write the full query on one line
# ACUMULADO DEPARTAMENTOS POR SEXO
query_departamentos_sexo="""select FECHA_CORTE, DEPARTAMENTO, count (case when SEXO = 'MASCULINO' and DOSIS = 2 then 1 end) as DOSIS2_M, count (case when SEXO = 'FEMENINO' and DOSIS = 2 then 1 end) as DOSIS2_F from df group by DEPARTAMENTO"""
result_query_departamentos_sexo=ps.sqldf(query_departamentos_sexo,locals())
print(ps.sqldf(query_departamentos_sexo,locals()))

# ACUMULADO POR GRUPO ETARIO
bins = [18,20,30,40,50,60,70,80,df['EDAD'].max()+1]
labels = ['18 a 19 años','20 a 29 años','30 a 39 años','40 a 49 años','50 a 59 años','60 a 69 años','70 a 79 años','80 años a más']
poblacion_por_grupo_etario = [700000,1300000,2300000,3300000,4400000,5300000,5700000,900000] 
result_df_edades = df
result_df_edades.drop(['SEXO', 'FECHA_VACUNACION', 'DEPARTAMENTO'], axis=1, inplace=True)
result_df_edades['GRUPO_ETARIO'] = pd.cut(df['EDAD'], bins=bins, labels=labels, right=False)
result_query_edades = result_df_edades[result_df_edades.DOSIS == 2].groupby(['GRUPO_ETARIO'])["DOSIS"].count().reset_index()
result_query_edades['POBLACION']=poblacion_por_grupo_etario
result_query_edades['%']=round(result_query_edades['DOSIS']/result_query_edades['POBLACION']*100,2)
result_query_edades

col_poblacion_m=[219801,
594832,
220370,
735707,
341951,
727265,
550046,
686543,
184121,
384345,
488836,
678494,
1000002,
638228,
5119560,
531000,
98215,
102855,
140252,
1030975,
611616,
474458,
188152,
135675,
307596]

col_poblacion_f=[207005,
585806,
210366,
761731,
326262,
726446,
579808,
670532,
181196,
375922,
486346,
682973,
1016769,
672557,
5508910,
496559,
75596,
89885,
131652,
1016979,
626381,
425190,
182822,
115846,
281514]

result_query_departamentos_sexo['POB_M']=col_poblacion_m
result_query_departamentos_sexo['POB_F']=col_poblacion_f
result_query_departamentos['POBLACION']=result_query_departamentos_sexo['POB_M'] + result_query_departamentos_sexo['POB_F']

result_query_departamentos['INDICE']=round(result_query_departamentos['DOSIS2']/(result_query_departamentos['POBLACION']/100000)).astype('int')
a = result_query_departamentos_sexo['POB_M']/result_query_departamentos_sexo['POB_F']
result_query_departamentos_sexo['INDICE_M']=round(result_query_departamentos_sexo['DOSIS2_M']/(result_query_departamentos_sexo['POB_M']/(a*100000/(a+1)))).astype('int')
result_query_departamentos_sexo['INDICE_F']=round(result_query_departamentos_sexo['DOSIS2_F']/(result_query_departamentos_sexo['POB_F']/(100000/(a+1)))).astype('int')

result_query_dosis.to_csv('resultados/dosis1y2.csv')
result_query_acumulados.to_csv('resultados/acumulados1y2.csv')
result_query_departamentos.to_csv('resultados/departamentos.csv')
result_query_departamentos_sexo.to_csv('resultados/departamentos_sexo.csv')
result_query_edades.to_csv('resultados/dosis2_por_edades.csv')
