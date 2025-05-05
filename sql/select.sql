-- Get all recipes
SELECT * FROM recipes ORDER BY created_at DESC;

-- Get recipe by ID
SELECT * FROM recipes WHERE id = @id;

-- Search recipes
SELECT * FROM recipes 
WHERE name LIKE '%' + @search + '%' 
   OR description LIKE '%' + @search + '%'
   OR ingredients LIKE '%' + @search + '%'; 