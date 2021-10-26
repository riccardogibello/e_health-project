SELECT 'to_analyze', COUNT(*) FROM preliminary WHERE `check` is FALSE;

SELECT 'preliminary_apps', COUNT(*) FROM preliminary;

SELECT 'external_to_analyze', COUNT(*) FROM preliminary WHERE `check` IS FALSE and from_dataset IS FALSE
    UNION
SELECT 'external', COUNT(*) FROM preliminary WHERE from_dataset IS FALSE;

SELECT 'teacher_approved', COUNT(*) FROM app WHERE teacher_approved is TRUE;

#TOTAL APPS STATISTICS
SELECT 'all_apps', COUNT(*) FROM preliminary
    UNION
SELECT 'checked_apps', COUNT(*) FROM preliminary WHERE `check` IS TRUE
    UNION
SELECT 'to_check_apps', COUNT(*) FROM preliminary WHERE `check`IS FALSE
    UNION
SELECT 'apps_with_description', COUNT(*) FROM app
    UNION
SELECT 'teacher_approved_apps', COUNT(*) FROM app WHERE teacher_approved IS TRUE;


UPDATE preliminary SET `check` = TRUE WHERE `check` IS FALSE;

UPDATE preliminary SET `check` = FALSE WHERE `check` IS TRUE;




