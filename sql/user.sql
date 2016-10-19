-- /*CREATE USER batch@localhost IDENTIFIED BY '@dminpass'; 
--            selectuser@localhost IDENTIFIED BY 'select@dmin';
-- DROP USER selectuser@localhost;
-- CREATE USER selectuser@'%' IDENTIFIED BY 'select@dmin';*/

GRANT SELECT ON debug_green.* TO selectuser;
GRANT SELECT, UPDATE, INSERT ON debug_green.* TO batch@localhost;
GRANT SELECT ON debug_green.* TO selectuser@'%';
