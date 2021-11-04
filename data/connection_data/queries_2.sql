SELECT '# training apps', count(*) FROM app_features
	UNION
SELECT '# serious games human classified in training' , count(*) FROM app_features WHERE human_classified = 1
	UNION
SELECT '# teacher approved apps in training', count(*) FROM app_features WHERE teacher_approved = 1
	UNION
SELECT '# total apps extracted', count(*) FROM app;

DROP TABLE IF EXISTS `tmp_labeled_apps`;
CREATE TABLE `tmp_labeled_apps` (
  `app_id` varchar(100) UNIQUE NOT NULL,
  `human_classified` boolean
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
SELECT COUNT(*) FROM tmp_labeled_apps;

# import back in app_features all the labeled apps
# INSERT INTO app_features SELECT app_id, ..., human_classified FROM tmp_labeled_apps;

/*
================================================================================================================================================
THIS PART HAS TO BE UNCOMMENTED ONLY IF YOU NEED TO INVERT THE LABELS IN THE TABLE tmp_labeled_apps
*/
/*
USE `projectdatabase`;
DROP TABLE IF EXISTS `FALSE_labels`;
CREATE TABLE `FALSE_labels` 
	SELECT app_id FROM tmp_labeled_apps WHERE human_classified = 0;

DROP TABLE IF EXISTS `TRUE_labels`;
CREATE TABLE `TRUE_labels` 
	SELECT app_id FROM tmp_labeled_apps WHERE human_classified = 1;


UPDATE tmp_labeled_apps SET human_classified = 1 WHERE app_id IN (
																SELECT app_id FROM false_labels
															);

UPDATE tmp_labeled_apps SET human_classified = 0 WHERE app_id IN (
																SELECT app_id FROM true_labels
															);
                                                            
DROP TABLE IF EXISTS `FALSE_labels`;
DROP TABLE IF EXISTS `TRUE_labels`;

INSERT INTO labeled_app(app_id, human_classified) SELECT * FROM tmp_labeled_apps;
TRUNCATE tmp_labeled_apps;

SELECT COUNT(*) FROM labeled_app;

SELECT COUNT(*) FROM app_features WHERE app_features.app_id NOT IN (SELECT labeled_app.app_id FROM labeled_app); 

SELECT app_id FROM tmp_labeled_apps WHERE app_id NOT IN (SELECT app_id FROM labeled_app);
*/
/*
================================================================================================================================================
*/

/*
================================================================================================================================================
THIS IS THE PART USED IN ORDER TO MERGE THE LABELED APPS ALL IN ONE TABLE (app_features)
*/
/*
UPDATE app_features SET human_classified = True WHERE app_id IN (	SELECT app_id 
																	FROM labeled_app
                                                                    WHERE human_classified = True
																);
                                                                
UPDATE app_features SET human_classified = False WHERE app_id IN (	SELECT app_id 
																	FROM labeled_app
                                                                    WHERE human_classified = False
																);
TRUNCATE labeled_app;

-- Check if the import from labeled_app to app_features went smoothly. The two following counts must be equal, so only one will appear.
SELECT COUNT(*) FROM app_features WHERE (human_classified = True OR human_classified = False) AND app_id IN (	SELECT app_id
																												FROM labeled_app
																											)
	UNION
SELECT COUNT(*) FROM labeled_app WHERE human_classified = True OR human_classified = False;
*/
/*
================================================================================================================================================
*/