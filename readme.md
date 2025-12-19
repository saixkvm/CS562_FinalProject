# CS562 Project Demo

This is basic demo code we wrote during lecture #2 on 3/30/23. Logic is hardcoded for a basic SQL query containing a where clause. The query is executed and the results are displayed in a table.

Feel free to use this as the basis for your project. You can use this code as a starting point and modify it to fit your needs.

**Note:** Don't forget to copy .env.example to .env and update the values to match your environment.


# To test the queries,
Go to the sql.py file, and change sql_file to the correct sql file. So if you want to test input1_mf.txt, change sql_file to "input1_mf.sql"
If you want to generate a input, go to generator.py. In input_processing(), set input_file to the input txt file (ex: input_file = "input1_mf.txt"). Then at the bottom of the code, set  written_file to the input txt filename + "_generated.py" (ex: written_file="input1_mf_generated.py")