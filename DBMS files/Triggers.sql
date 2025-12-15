--Trigger occours when student types goes wrong
DELIMITER $$

CREATE TRIGGER check_student_gender_hostel
BEFORE INSERT ON student
FOR EACH ROW
BEGIN
    DECLARE hostel_type VARCHAR(10);
    
    -- 1. Get the type of the assigned hostel (Boys or Girls)
    SELECT Type INTO hostel_type 
    FROM hostel 
    WHERE Hostel_id = NEW.Hostel_id;
    
    -- 2. Check for Mismatches
    -- Case A: Male Student trying to enter a Girls Hostel
    IF NEW.Gender = 'Male' AND hostel_type = 'Girls' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Error: Cannot assign a Male student to a Girls hostel.';
    
    -- Case B: Female Student trying to enter a Boys Hostel
    ELSEIF NEW.Gender = 'Female' AND hostel_type = 'Boys' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Error: Cannot assign a Female student to a Boys hostel.';
    END IF;
END$$

DELIMITER ;

--Trigger occours when warden types goes wrong
DELIMITER $$

CREATE TRIGGER check_warden_gender_hostel
BEFORE INSERT ON warden
FOR EACH ROW
BEGIN
    DECLARE hostel_type VARCHAR(10);
    
    -- 1. Get the type of the assigned hostel
    SELECT Type INTO hostel_type 
    FROM hostel 
    WHERE Hostel_id = NEW.Hostel_id;
    
    -- 2. Validation Logic
    -- Case A: Male Warden assigned to Girls Hostel
    IF NEW.Gender = 'Male' AND hostel_type = 'Girls' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Violation: A Male Warden cannot be assigned to a Girls Hostel.';
        
    -- Case B: Female Warden assigned to Boys Hostel
    ELSEIF NEW.Gender = 'Female' AND hostel_type = 'Boys' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Violation: A Female Warden cannot be assigned to a Boys Hostel.';
    END IF;
END$$

DELIMITER ;