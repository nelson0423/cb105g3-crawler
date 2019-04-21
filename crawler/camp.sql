DROP TABLE `camp_db`.`camp_webs`;
DROP TABLE `camp_db`.`camp_tels`;
DROP TABLE `camp_db`.`camp_features`;
DROP TABLE `camp_db`.`camp_list`;

CREATE TABLE `camp_db`.`camp_list` (
  `camp_title` VARCHAR(45) NOT NULL,
  `camp_site` VARCHAR(45) NOT NULL,
  `addr` VARCHAR(100) NOT NULL,
  `latlong` VARCHAR(45) NOT NULL,
  `location` VARCHAR(45) NOT NULL,
  `style` VARCHAR(45) NOT NULL,
  `tags` VARCHAR(1000) NOT NULL,
  `fb_rating` DECIMAL(5,2) NOT NULL DEFAULT 0,
  PRIMARY KEY (`camp_title`));
-- ALTER TABLE `camp_db`.`camp_list`
-- ADD COLUMN `fb_rating` DECIMAL(5,2) NOT NULL DEFAULT 0 AFTER `tags`;

CREATE TABLE `camp_db`.`camp_features` (
  `camp_title` VARCHAR(45) NOT NULL,
  `feature` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`camp_title`, `feature`),
  CONSTRAINT `camp_title_features`
    FOREIGN KEY (`camp_title`)
    REFERENCES `camp_db`.`camp_list` (`camp_title`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION);

CREATE TABLE `camp_db`.`camp_tels` (
  `camp_title` VARCHAR(45) NOT NULL,
  `tel` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`camp_title`, `tel`),
  CONSTRAINT `camp_title_tels`
    FOREIGN KEY (`camp_title`)
    REFERENCES `camp_db`.`camp_list` (`camp_title`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION);

CREATE TABLE `camp_db`.`camp_webs` (
  `camp_title` VARCHAR(45) NOT NULL,
  `name` VARCHAR(500) NOT NULL,
  `url` VARCHAR(500) NULL,
  PRIMARY KEY (`camp_title`, `name`),
  CONSTRAINT `camp_title_webs`
    FOREIGN KEY (`camp_title`)
    REFERENCES `camp_db`.`camp_list` (`camp_title`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION);

----------------------------------------------------------------------------------
select l.camp_id, l.camp_title, f.feature
from camp_list l
left join camp_features f
on l.camp_id = f.camp_id
order by l.camp_id;

select l.camp_id, l.camp_title, t.tel
from camp_list l
left join camp_tels t
on l.camp_id = t.camp_id
order by l.camp_id;