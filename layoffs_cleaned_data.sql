

-- Data Cleaning: The cleaning of this dataset will increase my overall productivity as well as yield the highest quality data possible for when I perform the subsequent 
-- exploratory data analysis. 
--------------------
SELECT * FROM layoffs;

-- 1. Remove Duplicates
-- 2. Standardize the Data
-- 3. Null Values (blank values)
-- 4. Remove Any Columns 

-- Creating a copy/staging table from the raw table
CREATE TABLE layoffs_staging AS
SELECT * FROM layoffs;

-- 1.
SELECT * ,
ROW_NUMBER() OVER(
PARTITION BY company, 'location', industry, total_laid_off, 
	percentage_laid_off, date) 
	AS row_num
FROM layoffs_staging;

-- Identifying the duplicates 
WITH duplicate_cte AS (
SELECT * ,
ROW_NUMBER() OVER(
PARTITION BY company, "location", industry, total_laid_off, 
	percentage_laid_off, "date", stage, country, funds_raised_millions) AS row_num
FROM layoffs_staging
)
SELECT * FROM duplicate_cte
WHERE row_num > 1;

-- Verifying duplicate nature
SELECT * FROM layoffs_staging
WHERE company = 'Casper';


-- Deleting the duplicates
CREATE TABLE IF NOT EXISTS public.layoffs_staging2
(
    company text COLLATE pg_catalog."default",
    location text COLLATE pg_catalog."default",
    industry text COLLATE pg_catalog."default",
    total_laid_off integer,
    percentage_laid_off text COLLATE pg_catalog."default",
    date text COLLATE pg_catalog."default",
    stage text COLLATE pg_catalog."default",
    country text COLLATE pg_catalog."default",
    funds_raised_millions numeric,
	row_num INT
) TABLESPACE pg_default;

SELECT * FROM layoffs_staging2
WHERE row_num > 1;

INSERT INTO layoffs_staging2
SELECT * ,
ROW_NUMBER() OVER(
PARTITION BY company, "location", industry, total_laid_off, 
	percentage_laid_off, "date", stage, country, funds_raised_millions) AS row_num
FROM layoffs_staging;
-- Now a new table has been created with a row_num column. We can delete the rows
-- with a value of 2 (duplicates)
DELETE FROM layoffs_staging2
WHERE row_num > 1;

-- Duplicates have now been removed
SELECT * FROM layoffs_staging2
WHERE row_num > 1;

SELECT * FROM layoffs_staging2;

-- 2. Standardizing Data
SELECT company, TRIM(company)
FROM layoffs_staging2;

-- Removing whitespace
UPDATE layoffs_staging2
SET company = TRIM(company);

SELECT * 
FROM layoffs_staging2
WHERE industry LIKE 'Crypto%';

UPDATE layoffs_staging2
SET industry = 'Crypto'
WHERE industry LIKE 'Crypto%';

SELECT DISTINCT industry 
FROM layoffs_staging2;


SELECT DISTINCT country, TRIM(TRAILING '.' FROM country)
FROM layoffs_staging2
ORDER BY 1;

UPDATE layoffs_staging2 
SET country = TRIM(TRAILING '.' FROM country)
WHERE country LIKE 'United States%';

-- Converting the date column from text to date datatype
SELECT "date",
TO_DATE("date", 'MM/DD/YYYY')
FROM layoffs_staging2;

UPDATE layoffs_staging2
SET "date" = TO_DATE("date", 'MM/DD/YYYY');


ALTER TABLE layoffs_staging2
ALTER COLUMN "date" TYPE DATE USING "date"::DATE;

SELECT * 
FROM layoffs_staging2;

-- 3. Null Values (blank values)
SELECT * FROM 
layoffs_staging2
WHERE total_laid_off IS NULL
AND percentage_laid_off IS NULL;

UPDATE layoffs_staging2
SET industry = NULL
WHERE industry = '';

SELECT *
FROM layoffs_staging2
WHERE industry IS NULL 
OR industry = '';

SELECT * 
FROM layoffs_staging2
WHERE company LIKE 'Bally%';

SELECT * FROM layoffs_staging2 t1
JOIN layoffs_staging2 t2
    ON t1.company = t2.company
	AND t1.location = t2.location
WHERE (t1.industry IS NULL OR t1.industry = '')
AND t2.industry IS NOT NULL;

-- t1 is to be populated by t2
UPDATE layoffs_staging2 AS t1
SET industry = t2.industry
FROM layoffs_staging2 AS t2
WHERE t1.company = t2.company
AND t1.industry IS NULL
AND t2.industry IS NOT NULL;

SELECT * FROM layoffs_staging2;

-- Rows where total_laid_off and percentage_laid_off are both null
SELECT * FROM 
layoffs_staging2
WHERE total_laid_off IS NULL
AND percentage_laid_off IS NULL;

-- Deleting the rows mentioned above (unreliable data)
DELETE 
FROM layoffs_staging2
WHERE total_laid_off IS NULL
AND percentage_laid_off IS NULL;

SELECT * FROM layoffs_staging2;

-- 4. Removing Column(s)
ALTER TABLE layoffs_staging2
DROP COLUMN row_num;

SELECT * FROM layoffs_staging2;

-- The data has been cleaned! Exploratory data analysis is now appropriate 
--------------------
