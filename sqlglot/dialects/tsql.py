from sqlglot import exp
from sqlglot.dialects.dialect import Dialect, rename_func
from sqlglot.dialects.mysql import MySQL
from sqlglot.generator import Generator
from sqlglot.parser import Parser
from sqlglot.tokens import Tokenizer, TokenType


class TSQL(Dialect):
    null_ordering = "nulls_are_small"
    time_format = "'yyyy-mm-dd hh:mm:ss'"

    class Tokenizer(Tokenizer):
        QUOTES = ["'"]
        IDENTIFIERS = ['"', ("[", "]")]

        KEYWORDS = {
            **Tokenizer.KEYWORDS,
            "BIT": TokenType.BOOLEAN,
            "REAL": TokenType.FLOAT,
            "NTEXT": TokenType.TEXT,
            "SMALLDATETIME": TokenType.DATETIME,
            "DATETIME2": TokenType.DATETIME,
            "DATETIMEOFFSET": TokenType.TIMESTAMPTZ,
            "TIME": TokenType.TIMESTAMP,
            "VARBINARY": TokenType.BINARY,
            "IMAGE": TokenType.IMAGE,
            "MONEY": TokenType.MONEY,
            "SMALLMONEY": TokenType.SMALLMONEY,
            "ROWVERSION": TokenType.ROWVERSION,
            "UNIQUEIDENTIFIER": TokenType.UNIQUEIDENTIFIER,
            "XML": TokenType.XML,
            "SQL_VARIANT": TokenType.VARIANT,
        }

    class Parser(Parser):
        FUNCTIONS = {
            **Parser.FUNCTIONS,
            "CHARINDEX": exp.StrPosition.from_arg_list,
        }

        def _parse_convert(self):
            to = self._parse_types()
            self._match(TokenType.COMMA)
            this = self._parse_field()
            return self.expression(exp.Cast, this=this, to=to)
        
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
        exp.StrAgg: lambda self, e: f"""STRING_AGG({self.sql(e, "this")}, {self.sql(e, "separator") or "','"})""",
        exp.GroupConcat: rename_func("STRING_AGG"),
        exp.Length: lambda self, e: f"""LEN({self.sql(e, "this")})""",

        # TODO: Check Introducers concept in TSQL, to replace e.name with. For now, empty is good enough. 
        exp.Introducer: lambda self, e: f"""{str(e).replace(e.name, "")}"""
        }

        TYPE_MAPPING = {
            **Generator.TYPE_MAPPING,
            exp.DataType.Type.BOOLEAN: "BIT",
            exp.DataType.Type.INT: "INTEGER",
            exp.DataType.Type.DECIMAL: "NUMERIC",
            exp.DataType.Type.DATETIME: "DATETIME2",
            exp.DataType.Type.VARIANT: "SQL_VARIANT",
        }
