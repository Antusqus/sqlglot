from itertools import count
from os import error
from pathlib import Path
from sqlglot import diff, parse_one
from sqlglot import exp
import sqlglot
from sqlglot.errors import ErrorLevel
from tests.dialects.test_mysql import TestMySQL

mySQL_statement: str =\
""" 
select `a`.`actor_id` AS `actor_id`,`a`.`first_name` AS `first_name`,`a`.`last_name` AS `last_name`,group_concat(distinct concat(`c`.`name`,': ',(select group_concat(`f`.`title` order by `f`.`title` ASC separator ', ') from ((`sakila`.`film` `f` join `sakila`.`film_category` `fc` on((`f`.`film_id` = `fc`.`film_id`))) join `sakila`.`film_actor` `fa` on((`f`.`film_id` = `fa`.`film_id`))) where ((`fc`.`category_id` = `c`.`category_id`) and (`fa`.`actor_id` = `a`.`actor_id`)))) order by `c`.`name` ASC separator '; ') AS `film_info` from (((`sakila`.`actor` `a` left join `sakila`.`film_actor` `fa` on((`a`.`actor_id` = `fa`.`actor_id`))) left join `sakila`.`film_category` `fc` on((`fa`.`film_id` = `fc`.`film_id`))) left join `sakila`.`category` `c` on((`fc`.`category_id` = `c`.`category_id`))) group by `a`.`actor_id`,`a`.`first_name`,`a`.`last_name`
"""
def main():
    try:
        # print(sqlglot.transpile(mySQL_statement, read="mysql",write="mysql", pretty= True)[0])

        # exit()
        # filename = "customer_list.sql"
        abs_path = Path.cwd()
        rel_path = f"queries/ddl_queries/"

        query: str
        Path(abs_path,rel_path).mkdir(parents=True,exist_ok=True)
        files = Path(abs_path,rel_path).glob("*")
        tmp_filter = [""]
        
        transpile_path = Path(abs_path, rel_path, "transpiled/")
        transpile_path.mkdir(parents=True,exist_ok=True)
        
        transpiled_ast_path = Path(transpile_path, "ast/")
        transpiled_ast_path.mkdir(parents=True,exist_ok=True)

        for file in files:
            if not file.is_dir():
                if f"{file.name}" not in tmp_filter:
                    with open(file, "r") as f:
                        query = f.read()
                        f.close()

                    print(f"Transpiling: {file.name}")
                    transpiled_statement = sqlglot.transpile(query, read="mysql", write="tsql", pretty = True, error_level=ErrorLevel.IGNORE)
                    for item in transpiled_statement:
                        transpiled_ast = repr(sqlglot.parse_one(item, read="tsql"))

                        with open(Path(transpile_path, file.name), "w") as wf:
                            wf.writelines(item)
                            wf.close()
                        with open(Path(transpiled_ast_path,file.name), "w") as wx:
                            wx.writelines(transpiled_ast)
                            wx.close()
                else:
                    print(f"{file.name} is filtered. Skipping.")


        # trans_parsed_statement = repr(parse_one(transpiled_statement[0], read="tsql"))
        # print(trans_parsed_statement.split(parsed_statement))
        # newtest = TestMySQL("test_introducers")

        # print(newtest())
    except error as e:
        print(e)
        
if __name__ == "__main__":
    main()