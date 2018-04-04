# CPrefSQL
CPrefSQL for PostgreSQL

Installation:
- The installation can be done by "install" script
- Use "install -?" to view instructions

Notes:
- Values of CHAR(N) fields have extra spaces. CPrefSQL functions do not remove
  this spaces. Queries must be remove spaces on this field by using TRIM()
  function
