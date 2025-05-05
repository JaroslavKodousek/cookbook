UPDATE recipes 
SET name = @name,
    description = @description,
    ingredients = @ingredients,
    category = @category,
    type = @type
WHERE id = @id; 