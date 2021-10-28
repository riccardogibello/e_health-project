set @row_num=0;
INSERT INTO category
	SELECT (@row_num:=@row_num+1) AS serial_num, category_id FROM 	(
																		SELECT DISTINCT category_id
																		FROM app
																	) AS tmp_table
		UNION 
	SELECT DISTINCT (@row_num:=@row_num+1) AS serial_num, 'OTHER';

DROP TABLE IF EXISTS app_tmp;
CREATE TABLE app_tmp
	SELECT app_id, app_name, category, score, rating, category_id, developer_id, teacher_approved FROM app;