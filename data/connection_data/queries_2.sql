SELECT '# training apps', count(*) FROM app_features
	UNION
SELECT '# serious games human classified in training' , count(*) FROM app_features WHERE human_classified = 1
	UNION
SELECT '# teacher approved apps in training', count(*) FROM app_features WHERE teacher_approved = 1
	UNION
SELECT '# total apps extracted', count(*) FROM app;

CREATE TABLE tmp_labeled_apps
	SELECT app_id, human_classified FROM app_features;
SELECT COUNT(*) FROM tmp_labeled_apps;

# import back in app_features all the labeled apps
INSERT INTO app_features SELECT app_id, ..., human_classified FROM tmp_labeled_apps;

/*
================================================================================================================================================
THIS PART HAS TO BE UNCOMMENTED ONLY IF YOU NEED TO INVERT THE LABELS IN THE TABLE labeled_app
*/
/*
USE `projectdatabase`;
DROP TABLE IF EXISTS `FALSE_labels`;
CREATE TABLE `FALSE_labels` 
	SELECT app_id FROM labeled_app WHERE human_classified = 0;

DROP TABLE IF EXISTS `TRUE_labels`;
CREATE TABLE `TRUE_labels` 
	SELECT app_id FROM labeled_app WHERE human_classified = 1;


UPDATE app_features SET human_classified = 1 WHERE app_id IN (
																SELECT app_id FROM false_labels
															);

UPDATE app_features SET human_classified = 0 WHERE app_id IN (
																SELECT app_id FROM true_labels
															);
                                                            
DROP TABLE IF EXISTS `FALSE_labels`;
DROP TABLE IF EXISTS `TRUE_labels`;
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