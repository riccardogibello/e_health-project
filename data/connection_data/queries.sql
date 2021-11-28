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

SELECT DISTINCT content_rating FROM app;

# PROGRESS
SELECT  'ALL_APPS', COUNT(*) FROM preliminary
    UNION
SELECT  'CONTROLLED APPS', COUNT(*) FROM preliminary WHERE preliminary.`check` IS TRUE
    UNION
SELECT  'TO_CHECK APPS', COUNT(*) FROM preliminary WHERE preliminary.`check` IS FALSE
    UNION
SELECT  'FROM DATASET TO CHECK', COUNT(*) FROM preliminary WHERE preliminary.`check` IS FALSE AND preliminary.from_dataset IS TRUE
    UNION
SELECT  'EXTERNAL TO CHECK', COUNT(*) FROM preliminary WHERE preliminary.`check` IS FALSE AND preliminary.from_dataset IS FALSE
    UNION
SELECT  'TO_CLASSIFY APPS', COUNT(*) FROM app
    UNION
SELECT 'TRAINING SET', COUNT(*) FROM labeled_app
    UNION
SELECT 'TRAINING SERIOUS', COUNT(*) FROM labeled_app WHERE human_classified IS TRUE
    UNION
SELECT 'TRAINING NOT SERIOUS', COUNT(*) FROM labeled_app WHERE human_classified IS FALSE
    UNION
SELECT 'DEVELOPERS', COUNT(*) FROM developer;


UPDATE preliminary SET `check` = TRUE WHERE `check` IS FALSE;

UPDATE preliminary SET `check` = FALSE WHERE `check` IS TRUE;

UPDATE preliminary SET `check` = FALSE WHERE app_id IN (
    SELECT app_id FROM app
    );

UPDATE labeled_app SET human_classified = NULL WHERE human_classified IS NOT NULL;


SELECT 'TOTAL_APPS', COUNT(*) FROM app
    UNION
SELECT 'APPS_NO_SCORE', COUNT(*) FROM app WHERE score = 0
    UNION
SELECT 'APPS_DANGEROUS_CONTENT', COUNT(*) FROM app WHERE content_rating = 'Adults only 18+' OR content_rating = 'Mature 17+' OR content_rating = 'Unrated' OR content_rating_description IS NOT NULL
    UNION
SELECT 'NOT_UPDATED_APPS AFTER 2019', COUNT(*) FROM app WHERE last_update < 1546300800
    UNION
SELECT 'NOT_UPDATED_APPS AFTER 2020', COUNT(*) FROM app WHERE last_update < 1577836800
    UNION
SELECT 'NOT_UPDATED_APPS AFTER 2021', COUNT(*) FROM app WHERE last_update < 1609459200;

# 1546300800 - Tuesday 1 January 2019 00:00:00
# 1577836800 - Wednesday 1 January 2020 00:00:00
# 1609459200 - Friday 1 January 2021 00:00:00


#With ratings, no dangerous and updated >2020
SELECT 'SELECTION 1', COUNT(*) FROM app WHERE score > 0  AND NOT content_rating = 'Adults only 18+' AND
                                                NOT content_rating = 'Mature 17+' AND NOT content_rating = 'Unrated' AND last_update > 1577836800
    UNION
#With ratings, no dangerous and updated >2019
SELECT 'SELECTION 2', COUNT(*) FROM app WHERE score > 0 AND NOT content_rating = 'Adults only 18+' AND
                                                NOT content_rating = 'Mature 17+' AND NOT content_rating = 'Unrated' AND last_update > 1546300800
    UNION
#No dangerous and updated >2019
SELECT 'SELECTION 3', COUNT(*) FROM app WHERE NOT content_rating = 'Adults only 18+' AND
                                                NOT content_rating = 'Mature 17+' AND NOT content_rating = 'Unrated' AND last_update > 1546300800
    UNION
#No dangerous, updated > 2019 and at least 500 installs
SELECT 'SELECTION 4', COUNT(*) FROM app WHERE installs > 499 AND NOT content_rating = 'Adults only 18+' AND
                                                NOT content_rating = 'Mature 17+' AND NOT content_rating = 'Unrated' AND last_update > 1546300800;



#QUERY CREATING "labeled_app" TABLE
TRUNCATE TABLE labeled_app;

INSERT INTO labeled_app(app_id)
SELECT app_id FROM app WHERE teacher_approved IS TRUE ORDER BY RAND() LIMIT 300;
INSERT INTO labeled_app(app_id)
SELECT app_id FROM app WHERE teacher_approved IS FALSE ORDER BY RAND() LIMIT 900;


INSERT IGNORE INTO preliminary(app_id) SELECT app_id FROM app;

TRUNCATE TABLE app;




