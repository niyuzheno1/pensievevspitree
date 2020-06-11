# your code goes here

#!/usr/bin/env python
# coding: utf-8

# In[1]:


from pyspark.context import SparkContext
from pyspark import SparkConf, StorageLevel
from pyspark.sql.session import SparkSession
from pyspark.sql.functions import *
from pyspark.sql import Row

spark = SparkSession.builder.appName("CS236 project").getOrCreate()
sc = spark.sparkContext

def opr(x,y):
    switcher = {'A': 6, 'B': 12, 'C': 18, 'D': 24, 'E': 12, 'F': 24, 'G': 24, 'H': 0, 'I': 0, '9' : 0}
    return float(x)*float(switcher[y])

def cutzero(s):
    return s.lstrip('0')

def clear(x):
    s = {}
    s['USAF'] = cutzero(x[0])
    s['WBAN'] = x[1]
    s['YEARMODA'] = x[2]
    s['PRCP'] = (opr(x[-3][0:-1],x[-3][-1])) 
    return Row(**s)

def fyear(s):
    s = s.asDict()
    x = s['YEARMODA'][4:6] 
    del s['YEARMODA']
    month = { '01' : "January",'02' : "February", '03' : "March",  '04' : "April", '05' : "May", '06' : "June",'07' : "July",
       '08' : "August", '09' : "September", '10' : "October", '11' : "November", '12' : "December"
            }
    s['Month'] = month[x] 
    return Row(**s)

def diff(x):
    x = x.asDict()
    x['Variation'] = x['PRCPmax']-x['PRCPmin']
    del x['PRCPmax']
    del x['PRCPmin']
    return Row(**x)


# In[3]:


df = spark.read.format("csv").option("header", "true").load("/opt/spark-data/WeatherStationLocations.csv")
df2 = df.select("USAF","WBAN","CTRY","STATE","BEGIN","END").filter(df["CTRY"] == "US").sort("STATE", ascending=False)
### question 1
print("Question 1: group stations by state")
df2.show()
df2.coalesce(1).write.option("header","true").csv("Q1")


# In[7]:


rdd1 = sc.textFile("/opt/spark-data/2006.txt").map(lambda s: s.split()).filter(lambda s: s[0] != 'STN---').map(clear)
rdd2 = sc.textFile("/opt/spark-data/2007.txt").map(lambda s: s.split()).filter(lambda s: s[0] != 'STN---').map(clear)
afile =rdd1.toDF()
afiles = afile.join(df2,(afile.USAF == df2.USAF) & (afile.YEARMODA <= df2.END) & (afile.YEARMODA >= df2.BEGIN))
afiles.persist(StorageLevel.MEMORY_AND_DISK)
bfile =rdd2.toDF()
bfiles = bfile.join(df2,(bfile.USAF == df2.USAF) & (bfile.YEARMODA <= df2.END) & (bfile.YEARMODA >= df2.BEGIN))
bfiles.persist(StorageLevel.MEMORY_AND_DISK)

rdd3 = sc.textFile("/opt/spark-data/2008.txt").map(lambda s: s.split()).filter(lambda s: s[0] != 'STN---').map(clear)
rdd4 = sc.textFile("/opt/spark-data/2009.txt").map(lambda s: s.split()).filter(lambda s: s[0] != 'STN---').map(clear)
cfile =rdd3.toDF()
cfiles = cfile.join(df2,(cfile.USAF == df2.USAF) & (cfile.YEARMODA <= df2.END) & (cfile.YEARMODA >= df2.BEGIN))
cfiles.persist(StorageLevel.MEMORY_AND_DISK)

dfile =rdd4.toDF()
dfiles = dfile.join(df2,(dfile.USAF == df2.USAF) & (dfile.YEARMODA <= df2.END) & (dfile.YEARMODA >= df2.BEGIN))
dfiles.persist(StorageLevel.MEMORY_AND_DISK)
df11 = afiles.union(bfiles)
df11.persist(StorageLevel.MEMORY_AND_DISK)
df11 = df11.union(cfiles)
df11.persist(StorageLevel.MEMORY_AND_DISK)
df11 = df11.union(dfiles)
df11.persist(StorageLevel.MEMORY_AND_DISK)

rdd12 = df11.rdd.map(fyear)
groupd = rdd12.toDF(sampleRatio=0.2).groupby('STATE','Month')
df13 = groupd.avg('PRCP').withColumnRenamed('avg(PRCP)','PRCP')
df13.cache()
### Q2
print("Question 2: average precipitation recorded for each month by each state")
df13.show()
df13.coalesce(1).write.option("header","true").csv("Q2")


# In[4]:


dfmax = df13.groupby('STATE').agg({"PRCP": "max"}).withColumnRenamed('max(PRCP)','PRCPmax')
dfmin = df13.groupby('STATE').agg({"PRCP": "min"}).withColumnRenamed('min(PRCP)','PRCPmin')

dfmax1 = dfmax.join(df13, (df13.PRCP== dfmax.PRCPmax) & (df13.STATE== dfmax.STATE)).select(df13.STATE,'Month','PRCP')
dfmin1 = dfmin.join(df13, (df13.PRCP== dfmin.PRCPmin) & (df13.STATE== dfmin.STATE)).select(df13.STATE,'Month','PRCP')

### question 3
print("Question 3: ")
print("months with the highest averages")
dfmax1.show()
dfmax1.coalesce(1).write.option("header","true").csv("Q3/highest")
print("months with the lowest averages")
dfmin1.show()
dfmin1.coalesce(1).write.option("header","true").csv("Q3/lowest")


# In[5]:


df14 = dfmax.join(dfmin, 'STATE')



var = df14.rdd.map(diff).toDF(sampleRatio=0.2).sort("Variation", ascending=True)
### question 4
print("order the states by the difference between the highest and lowest month")
var.show()
var.coalesce(1).write.option("header","true").csv("Q4")

