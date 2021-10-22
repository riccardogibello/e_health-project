SELECT '', ''
	UNION
SELECT 'total_apps_to_be_analysed', COUNT(*) FROM preliminary WHERE preliminary.check = 0
	UNION
SELECT 'total_apps_with_details', COUNT(*) FROM app
	UNION
SELECT 'teacher_approved_apps', COUNT(*) FROM app WHERE teacher_approved = 1;