#Department-wise Employee Strength
MV_DEPTSTRENGTH = """select 
MONTH,
YEAR,
EMPDEPT,
TOTAL,
NCATEGORY,CATEGORY,COMPANYNAME , COMPANYCODE
from MV_DEPTSTRENGTH"""

#GRN Dashboard
MV_GRN_DATA = """SELECT companycode as "Companycode",companyname as "Companyname",PROJECTCODE as "Project",YEAR as "Year",MONTH as "Month",GRNAMOUNT as "Amount" FROM MV_GRN_DATA"""

#lpo Dashboard
MV_LPODATA="""select companycode as "Companycode",companyname as "Companyname",YEAR as "Year",MONTH as "Month",PROJECT as "Project",AMOUNT as "Amount" from MV_LPODATA"""


MV_LPO_GRN_DATA="""select companycode as "Companycode",companyname as "Companyname", YEAR as "Year",MONTH as "Month", PROJECTCODE as "Project",PO_VALUE  as "PO_Value",GRN_VALUE as "GRN_Value" from MV_LPO_GRN_DATA"""

#Main Projects , Main Facilities
MV_LPO_GRN_NETVALUE="""select companycode as "Companycode",companyname as "Companyname", projectcode as "Project",po_net_value as "PO_Value",grn_net_value as "GRN_Value" from mv_lpo_grn_netvalue"""

#Top 20 Suppliers
PURCHASE = """select TRANSACTION_TYPE,
  DOCID,PONO,MRNO,BRANCHNAME,LOCATIONNAME,VENDORCODE,
  VENDORNAME,PROJECTCODE ,PROJECTNAME ,
  IPARENT,CATEGORYNAME,ITYPE,ITEMNAME  ,
  YEAR,MONTH,AMOUNT_OMR from mv_dashboard where transaction_type = 'GRN' or transaction_type = 'Direct Purchase' """

#Total Employee Strength Yearly,Monthly Labour strenght
MV_EMPSTRENGTH="""select COMPANY,EMPMAINCAT,NATIONALITY,YEAR,MONTH, MM,STRENGTH from MV_EMPSTRENGTH"""

#Yearly Employee Strength (IN/Out)
MV_INOUT_STRENGTH="""select EMPMAINCAT,YEAR as "Year",MONTH,TYPE,STRENGTH as "Total_Strength",Companyname , Companycode from MV_INOUT_STRENGTH"""

#Visa Expiry Report 
MV_VISA_EXPIRY="""SELECT EMPLOYEE_TYPE as "Employee_Type",EMPMAINCAT as "Employee_Category",YEAR as "Expiry_Year",MONTH as "Expiry_Month",TOTAL_EMP as "Total_by_Month",COMPANYNAME , COMPANYCODE FROM MV_VISA_EXPIRY"""

SALES = """SELECT TRANSACTION_TYPE,substr(COMPANY_NAME,1,10) COMPANY_NAME ,DOCID ,
  DOCDT ,PRODUCT_NAME , PRODUCT_GROUP,PRODUCT_CATEGORY,
  CUSTOMERNAME ,sum(NET_AMOUNT)NET_AMOUNT FROM VW_SALES
  group by TRANSACTION_TYPE,COMPANY_NAME,DOCID ,
  DOCDT ,PRODUCT_NAME , PRODUCT_GROUP,PRODUCT_CATEGORY,
  CUSTOMERNAME"""

LEDGER = """SELECT trunc(VCHDT,'YEAR') as VCHDT,TYPE,GROUPID,ACCOUNTNAME,CATEGORY,
SUBLEDGER, sum(AMOUNT) amount  from 
vw_Ledger
group by trunc(VCHDT,'YEAR'),TYPE,GROUPID,ACCOUNTNAME,CATEGORY,
SUBLEDGER
"""
CASH = """select ACCOUNTNAME ,PRVYCLOSINGM ,PRMCLOSING ,TODAYAMT 
  from VW_CASH"""

BANK = """select
  ACCOUNTNAME ,PRVYCLOSING ,
  PRMCLOSING,  TODAYAMT from vw_bank"""

CY_PY_EXPENSE = """select ACCOUNTNAME,VCHMONTHNO,PY_AMOUNT,CY_AMOUNT,
    PM_AMOUNT,CM_AMOUNT 
from VW_CURRANDPREVEXPENSE
"""

CY_PY_INCOME = """select COMPANYNAME,COMPANYCODE,ALIE,VCHMONTHNO,VCHSHORTMONTH,ACCOUNTNAME ,
CY_AMOUNT,PY_AMOUNT 
from VW_CURRANDPREVINCOME
WHERE ALIE IN ('i')
    """

FIN = """select GROUPACC,ALIE,ACCOUNTNAME,BRANCHCODE,BRANCHNAME,CATEGORY,TOTAL_AMT,TOTAL_ASSETAMT,
TOTAL_LIABILTYAMT,NETWORTH,CY_INCOME,CY_EXPENSE,PY_INCOME,PY_EXPENSE
from py_vw_finance """


EMPLOYEE = '''select  EMPMASTID,EMPID,EMPNAME,DOJ,NATIONALITY,
NCATEGORY,GENDER,EMPMAINCAT,RELIGION,
ASECTOR,JOBCODE,DEPARTMENT,DESIGNATION,
PROFESSION,DOR,GRADE from PY_EMPLOYEE'''

GP_COMPANY = '''select  branchname as Companyname from branch'''

GP_PROJECT='''select projectcode from projectmaster'''

GP_EMPCATEGORY = '''select distinct empmaincat from empmast'''

GP_YEAR = '''SELECT  2020+LEVEL AS A 
FROM DUAL CONNECT BY LEVEL <= TO_NUMBER(TO_CHAR(SYSDATE,'YYYY'))-2020
ORDER BY 1 DESC'''

QR_SESSIONID="""select sessionid,username
from (SELECT *
FROM axpertlog
order by callfinished desc
FETCH FIRST 100 ROW ONLY)
group by sessionid,username"""

QR_DASHBOARD_ACCESS = """SELECT username, dashboardaccess, superuser, sales, finance, purchase, hr
FROM dashboard_access
where username <> 'admin'
ORDER BY username"""

QR_SYNC_USERS = """INSERT INTO dashboard_access (username, dashboardaccess, superuser, sales, finance, purchase, hr)
SELECT u.username, 'F', 'F', 'F', 'F', 'F', 'F'
FROM axusers u
WHERE NOT EXISTS (
    SELECT 1 
    FROM dashboard_access da 
    WHERE da.username = u.username
) AND u.username is not null
and 1=2 """

QR_AXUSERS_ONLY = """SELECT username 
FROM axusers u
WHERE NOT EXISTS (
    SELECT 1 
    FROM dashboard_access da 
    WHERE da.username = u.username
) AND u.username IS NOT NULL AND u.username <> 'admin' 
ORDER BY username"""