CREATE TABLE `camp_db`.`camp_list` (
  `camp_id` INT NOT NULL AUTO_INCREMENT,
  `camp_title` VARCHAR(45) NOT NULL,
  `camp_site` VARCHAR(45) NOT NULL,
  `addr` VARCHAR(100) NOT NULL,
  `latlong` VARCHAR(45) NOT NULL,
  `location` VARCHAR(45) NOT NULL,
  `style` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`camp_id`),
  UNIQUE INDEX `camp_title_UNIQUE` (`camp_title` ASC) VISIBLE);

CREATE TABLE `camp_db`.`camp_features` (
  `camp_id` INT NOT NULL,
  `feature` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`camp_id`, `feature`),
  CONSTRAINT `camp_id_features`
    FOREIGN KEY (`camp_id`)
    REFERENCES `camp_db`.`camp_list` (`camp_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION);

CREATE TABLE `camp_db`.`camp_tels` (
  `camp_id` INT NOT NULL,
  `tel` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`camp_id`, `tel`),
  CONSTRAINT `camp_id_tels`
    FOREIGN KEY (`camp_id`)
    REFERENCES `camp_db`.`camp_list` (`camp_id`)
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