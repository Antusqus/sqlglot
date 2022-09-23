from sqlglot import exp
from sqlglot.dialects.dialect import Dialect, rename_func
from sqlglot.generator import Generator
from sqlglot.parser import Parser
from sqlglot.tokens import Tokenizer, TokenType

class SQLServer(Dialect):
    class Tokenizer(Tokenizer):
        QUOTES = ['"']
        # IDENTIFIERS = ["`"]
        ESCAPE = "'"

        KEYWORDS = {
            **Tokenizer.KEYWORDS,
            "INT64": TokenType.BIGINT,
            "FLOAT64": TokenType.DOUBLE,
        }
    
    class Parser(Parser):

        FUNCTION_PARSERS = {
            **Parser.FUNCTION_PARSERS,
            "STRING_AGG": lambda self: self.expression(
                exp.StrAgg,
                this=self._parse_lambda(),
                separator=self._match(TokenType.COMMA) and self._parse_field(),
            ),
        }

    class Generator(Generator):
        TRANSFORMS = {
            **Generator.TRANSFORMS,
            exp.StrAgg: lambda self, e: f"""STRINGAGG({self.sql(e, "this")}, {self.sql(e, "separator") or "','"})""",
            exp.GroupConcat: rename_func("STRING_AGG"),
            exp.Length: lambda self, e: f"""LEN({self.sql(e, "this")})"""
            }

        TYPE_MAPPING = {
            exp.DataType.Type.TINYINT: "INT64",
            exp.DataType.Type.SMALLINT: "INT64",
            exp.DataType.Type.INT: "INT64",
            exp.DataType.Type.BIGINT: "INT64",
            exp.DataType.Type.DECIMAL: "NUMERIC",
            exp.DataType.Type.FLOAT: "FLOAT64",
            exp.DataType.Type.DOUBLE: "FLOAT64",
            exp.DataType.Type.BOOLEAN: "BOOL",
            exp.DataType.Type.TEXT: "STRING",
        }