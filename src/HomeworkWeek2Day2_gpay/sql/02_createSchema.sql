
drop table if exists gpay;;

CREATE TABLE gpay (
    id VARCHAR(20) PRIMARY KEY,
    vendor_id VARCHAR(20) NOT NULL,
    amount DECIMAL(15, 2) NOT NULL,
    status VARCHAR(20) NOT NULL,
    gpay_token VARCHAR(20) NOT NULL

    
);
