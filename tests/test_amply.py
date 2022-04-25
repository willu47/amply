import unittest
from io import StringIO

import pytest

from amply import amply
from amply.amply import (
    number,
    param_def_stmt,
    param_stmt,
    set_record,
    set_stmt,
    simple_data,
    single,
    subscript_domain,
    symbol,
)


class TestSubscript:
    def test_subscript(self):
        fixture = """
        {a, b, c}
        {enum}
        {REGION, YEAR}
        {REGION, TECHNOLOGY, YEAR}
        {r in REGION}
        {r in REGION, y in YEAR, g in GOLF}

        """
        success, result = subscript_domain.runTests(fixture)
        assert success

        assert result[0]

    def test_subscript_result(self):
        result = subscript_domain.parseString("{a, b, c}")
        assert result.asDict() == {"subscripts": ["a", "b", "c"]}

    def test_subscript_result_domain(self):
        result = subscript_domain.parseString("{a in A, b in B, c in C}")
        assert result.asDict() == {"subscripts": ["A", "B", "C"]}


class TestNumber:
    def test_not_number(self):
        fixture = """
        one
        _
        1e
        e2
        +
        Jan
        01Jan
        Jan_01
        01_Jan
        """
        result = number.runTests(fixture, failureTests=True)
        assert result[0]

    def test_number(self):
        fixture = """
        1
        1.1
        0.234
        +1e-049
        2
        00
        0.0
        """
        result = number.runTests(fixture)
        assert result[0]


class TestSymbol:
    def test_not_symbol(self):
        fixture = """
        1.1
        0.234
        +1e-049
        skj!adfk
        __12
        """
        result = symbol.runTests(fixture, failureTests=True)
        assert result[0]

    def test_symbol(self):
        fixture = """
        Jan

        01Jan

        Jan_01

        01_Jan
        """
        result = symbol.runTests(fixture)
        assert result[0]


class TestParameter:
    def test_param_def(self):
        fixture = """
        param Test{r in REGION, y in YEAR, g in GOLF};
        param square {x, y};
        param Test;
        param Test default 1;
        """
        success, results = param_def_stmt.runTests(fixture)

        assert success

        success, _ = param_stmt.runTests(fixture, failureTests=True)
        assert success

    def test_param_stmt(self):
        fixture = """
        param T := 4;

        param T := -4;

        param T := 0.04;

        param T := -0.04;

        param 01Jan := -0.04;

        param 01_Feb := -0.04;

        """
        result = param_stmt.runTests(fixture)
        assert result[0]

        result = param_def_stmt.runTests(fixture, failureTests=True)
        assert result[0]


class TestSet:
    def test_set_stmt(self):
        fixture = """
        set month := Jan Feb Mar Apr;

        set month := 01Jan 01_Feb Mar A_pr;

        set 1_2_month := 1 2 3 4;
        """
        result = set_stmt.runTests(fixture)
        assert result[0]

    @pytest.fixture()
    def setup(self):
        fixture = """
        Jan Feb Mar Apr

        01Jan 01_Feb Mar A_pr

        1 2 3 4
        """
        return fixture

    def test_set_record(self, setup):
        result = set_record.runTests(setup)
        assert result[0]

    def test_simple_data(self, setup):
        result = simple_data.runTests(setup)
        assert result[0]

    def test_single(self):
        fixture = """
        01Jan
        01
        Jan
        Jan_01
        01_Jan
        """
        result = single.runTests(fixture)
        assert result[0]


class AmplyTest(unittest.TestCase):
    def test_data(self):
        result = amply.Amply("param T := 4;")["T"]
        assert result == 4
        result = amply.Amply("param T := -4;")["T"]
        assert result == -4
        result = amply.Amply("param T := 0.04;")["T"]
        assert result == 0.04
        result = amply.Amply("param T := -0.04;")["T"]
        assert result == -0.04

    def test_set(self):
        result = amply.Amply("set month := Jan Feb Mar Apr;")["month"]
        assert result == ["Jan", "Feb", "Mar", "Apr"]

        result = amply.Amply("set month Jan Feb Mar Apr;")["month"]
        assert result == ["Jan", "Feb", "Mar", "Apr"]
        assert [i for i in result] == ["Jan", "Feb", "Mar", "Apr"]
        assert result != []

        assert "Jan" in result
        assert "Foo" not in result
        assert len(result) == 4

    def test_set_alphanumerical(self):
        result = amply.Amply("set month := 01Jan 01_Feb Mar A_pr;")["month"]
        assert result == ["01Jan", "01_Feb", "Mar", "A_pr"]

    def test_param_definition(self):
        result = amply.Amply("param T;")
        assert result != [4]

    def test_param(self):
        result = amply.Amply("param T := 4;")["T"]
        assert result != [4]

    def test_param_subscript(self):
        result = amply.Amply("param T{foo};param T := 1 2;")["T"]
        assert not (result == 2)
        assert result != 2

    def test_attr_access(self):
        result = amply.Amply("param T:= 4;").T
        assert result == 4

    def test_from_file(self):
        try:
            s = StringIO("param T:= 4;")
        except TypeError:
            s = StringIO(u"param T:= 4;")
        assert amply.Amply.from_file(s).T == 4

    def test_load_string(self):
        a = amply.Amply("param T:= 4; param X{foo};")
        a.load_string("param S := 6; param X := 1 2;")
        assert a.T == 4
        assert a.S == 6
        assert a.X[1] == 2

    def test_load_file(self):
        a = amply.Amply("param T:= 4; param X{foo};")
        try:
            s = StringIO("param S := 6; param X := 1 2;")
        except TypeError:
            s = StringIO(u"param S := 6; param X := 1 2;")
        a.load_file(s)
        assert a.T == 4
        assert a.S == 6
        assert a.X[1] == 2

    def test_empty_init(self):
        a = amply.Amply()
        a.load_string("param T := 4;")
        assert a.T == 4

    def test_set_dimen2(self):
        result = amply.Amply(
            """
            set twotups dimen 2;
            set twotups := (1, 2) (2, 3) (4, 2) (3, 1);
            """
        )["twotups"]
        assert result == [(1, 2), (2, 3), (4, 2), (3, 1)]

    def test_set_dimen_error(self):
        a = """
            set dim1 dimen 1;
            set dim1 := (1, 2) (2, 3) (3, 2);
            """
        self.assertRaises(amply.AmplyError, lambda: amply.Amply(a))

    def test_set_dimen2_noparen(self):
        result = amply.Amply(
            """
            set twotups dimen 2;
            set twotups := 1 2 2 3 4 2 3 1;
            """
        )["twotups"]
        assert result == [(1, 2), (2, 3), (4, 2), (3, 1)]

    def test_set_subscript(self):
        result = amply.Amply(
            """
            set days{months};
            set days[Jan] := 1 2 3 4;
            set days[Feb] := 5 6 7 8;
            """
        )["days"]
        j = result["Jan"]
        assert j == [1, 2, 3, 4]
        f = result["Feb"]
        assert f == [5, 6, 7, 8]

    def test_set_subscript2(self):
        result = amply.Amply(
            """
            set days{months, days};
            set days[Jan, 3] := 1 2 3 4;
            set days[Feb, 'Ham '] := 5 6 7 8;
            """
        )["days"]
        j = result["Jan"][3]
        assert j == [1, 2, 3, 4]
        f = result["Feb"]["Ham "]
        assert f == [5, 6, 7, 8]

    def test_set_subscript2_tuples(self):
        result = amply.Amply(
            """
            set days{months, days};
            set days[Jan, 3] := 1 2 3 4;
            set days[Feb, 'Ham '] := 5 6 7 8;
            """
        )["days"]
        j = result["Jan", 3]
        assert j == [1, 2, 3, 4]
        f = result["Feb", "Ham "]
        assert f == [5, 6, 7, 8]

    def test_set_matrix(self):
        result = amply.Amply(
            """
            set A : 1 2 3 :=
                1   + - -
                2   + + -
                3   - + -
            ;
            """
        )
        a = result.A
        assert a == [(1, 1), (2, 1), (2, 2), (3, 2)]

    def test_set_matrix_tr(self):
        result = amply.Amply(
            """
            set A (tr) : 1 2 3 :=
                     1   + - -
                     2   + + -
                     3   - + -
            ;
            """
        )
        a = result.A
        assert a == [(1, 1), (1, 2), (2, 2), (2, 3)]

    def test_set_splice(self):
        result = amply.Amply(
            """
            set A dimen 3;
            set A := (1, 2, 3), (1, 1, *) 2 4 (3, *, *) 1 1;
            """
        )
        a = result.A
        assert a == [(1, 2, 3), (1, 1, 2), (1, 1, 4), (3, 1, 1)]

    def test_set_splice_matrix(self):
        result = amply.Amply(
            """
            set A dimen 3;
            set A (1, *, *) : 1 2 3 :=
                        1     + - -
                        2     + - +
                        3     - - -
                  (2, *, *) : 1 2 3 :=
                        1     + - +
                        2     - + -
                        3     - - +
            ;
            """
        )
        a = result.A
        assert a == [
            (1, 1, 1),
            (1, 2, 1),
            (1, 2, 3),
            (2, 1, 1),
            (2, 1, 3),
            (2, 2, 2),
            (2, 3, 3),
        ]

    def test_simple_params(self):
        result = amply.Amply("param T := 4;")["T"]
        assert result == 4

    def test_sub1_params(self):
        result = amply.Amply(
            """
            param foo {s};
            param foo := 1 Jan 2 Feb 3 Mar;
            """
        )
        j = result["foo"][1]
        assert j == "Jan"
        f = result["foo"][2]
        assert f == "Feb"

    def test_sub1_param_error(self):
        a = """
            param foo{s};
            param foo := 1 Jan 2 Feb 3;
            """
        self.assertRaises(amply.AmplyError, lambda: amply.Amply(a))

    def test_param_default(self):
        result = amply.Amply(
            """
            param foo {s} default 3;
            param foo := Jan 1 Feb 2 Mar 3;
            """
        )
        options = [("Jan", 1), ("Mar", 3), ("FOO", 3)]
        for name, value in options:
            self.assertEqual(result["foo"][name], value)

    def test_param_undefined(self):
        result = amply.Amply(
            """
            param foo {s} ;
            param foo := Jan 1 Feb 2 Mar 3;
            """
        )
        j = result["foo"]["Jan"]
        assert j == 1
        with self.assertRaises(KeyError):
            result["foo"]["Apr"]

    def test_sub2_params(self):
        result = amply.Amply(
            """
            param foo {s, t};
            param foo := 1 2 Hi 99 3 4;
            """
        )
        h = result["foo"][1][2]
        assert h == "Hi"
        f = result["foo"][99][3]
        assert f == 4

    def test_2d_param(self):
        result = amply.Amply(
            """
            param demand {item, location};
            param demand
                :   FRA DET LAN :=
            spoons  200 100 30
            plates  30  120 90
            cups    666 13  29 ;
            """
        )["demand"]

        options = [
            ("spoons", {"FRA": 200, "DET": 100, "LAN": 30}),
            ("plates", {"FRA": 30, "DET": 120, "LAN": 90}),
            ("cups", {"FRA": 666, "DET": 13, "LAN": 29}),
        ]
        for name, _dict in options:
            self.assertDictEqual(result[name], _dict)

    def test_2d_numeric_param(self):
        result = amply.Amply(
            """
            param square {x, y};
            param square : 1 2 :=
                4       4   8
                3       3   6
            ;
            """
        )["square"]
        f = result[4, 1]
        assert f == 4
        assert result[4, 2] == 8
        assert result[3, 1] == 3
        assert result[3, 2] == 6

    def test_2d_param_defaults(self):
        result = amply.Amply(
            """
            param demand {item, location};
            param demand default 42
                :   FRA DET LAN :=
            spoons  200 . 30
            plates  30  120 .
            cups    . .  29 ;
            """
        )["demand"]

        options = [
            ("spoons", {"FRA": 200, "DET": 42, "LAN": 30}),
            ("plates", {"FRA": 30, "DET": 120, "LAN": 42}),
            ("cups", {"FRA": 42, "DET": 42, "LAN": 29}),
        ]
        for name, _dict in options:
            self.assertDictEqual(result[name], _dict)

    def test_2tables(self):
        result = amply.Amply(
            """
            param demand {item, location};
            param demand default 42
                :   FRA DET LAN :=
            spoons  200 . 30
            plates  30  120 .
            cups    . .  29
            ;

            param square {foo, foo};
            param square
                :   A   B :=
            A       1   6
            B       6   36
            ;
            """
        )
        demand = result["demand"]
        options = [
            ("spoons", {"FRA": 200, "DET": 42, "LAN": 30}),
            ("plates", {"FRA": 30, "DET": 120, "LAN": 42}),
            ("cups", {"FRA": 42, "DET": 42, "LAN": 29}),
        ]
        for name, _dict in options:
            self.assertDictEqual(demand[name], _dict)

        square = result["square"]
        options = [
            ("A", {"A": 1, "B": 6}),
            ("B", {"A": 6, "B": 36}),
        ]
        for name, _dict in options:
            self.assertDictEqual(square[name], _dict)

    def test_2d_param_transpose(self):
        result = amply.Amply(
            """
            param demand {location, item};
            param demand default 42 (tr)
                :   FRA DET LAN :=
            spoons  200 . 30
            plates  30  120 .
            cups    . .  29 ;
            """
        )["demand"]

        self.assertEqual(result["FRA"], {"spoons": 200, "plates": 30, "cups": 42})
        self.assertEqual(result["DET"], {"spoons": 42, "plates": 120, "cups": 42})
        self.assertEqual(result["LAN"], {"spoons": 30, "plates": 42, "cups": 29})

    def test_2d_slice1(self):
        result = amply.Amply(
            """
            param demand {location, item};
            param demand :=
                [Jan, *] Foo 1 Bar 2;
            """
        )["demand"]
        f = result["Jan"]["Foo"]
        assert f == 1
        assert result["Jan"]["Bar"] == 2

    def test_3d_slice2(self):
        result = amply.Amply(
            """
            param trans_cost{src, dest, product};
            param trans_cost :=
                [*,*,bands]: FRA DET LAN :=
                    GARY     30  10  8
                    CLEV     22  7   10
                [*,*,coils]: FRA DET LAN :=
                    GARY     39  14  11
                    CLEV     27  9   12
                [*,*,plate]: FRA DET LAN :=
                    GARY     41  15  12
                    CLEV     29  9   13
            ;
            """
        )["trans_cost"]

        f = result["GARY"]["FRA"]["bands"]
        assert f == 30
        assert result["GARY"]["DET"]["plate"] == 15
        assert result["CLEV"]["LAN"]["coils"] == 12

    def test_3d_slice2b(self):
        result = amply.Amply(
            """
            param trans_cost{src, product, dest};
            param trans_cost :=
                [*,bands,*]: FRA DET LAN :=
                    GARY     30  10  8
                    CLEV     22  7   10
                [*,coils,*]: FRA DET LAN :=
                    GARY     39  14  11
                    CLEV     27  9   12
                [*,plate,*]: FRA DET LAN :=
                    GARY     41  15  12
                    CLEV     29  9   13
            ;
            """
        )["trans_cost"]

        f = result["GARY"]["bands"]["FRA"]
        assert f == 30
        assert result["GARY"]["plate"]["DET"] == 15
        assert result["CLEV"]["coils"]["LAN"] == 12

    def test_3d_slide2c(self):
        amply.Amply(
            """
            set REGION := Kenya;
            set TECHNOLOGY := TRLV_1_0;
            set YEAR := 2016 2017 2018 2019 2020;
            param Peakdemand {REGION,TECHNOLOGY,YEAR};
            param Peakdemand default 1 :=
            [Kenya,*,*]:
            2016 2017 2018 2019 2020 :=
            TRLV_1_0 0 0 0 0.035503748 0.073847796
            ;
            """
        )

    def test_single_tabbing_data(self):
        result = amply.Amply(
            """
            set elem;
            param init_stock{elem};
            param cost{elem};
            param value{elem};
            param : init_stock  cost    value :=
            iron    7           25      1
            nickel  35          3       2
            ;
            """
        )
        s = result["init_stock"]
        assert s == {"iron": 7, "nickel": 35}
        assert result["cost"] == {"iron": 25, "nickel": 3}
        assert result["value"] == {"iron": 1, "nickel": 2}

    def test_single_tabbing_data_with_set(self):
        result = amply.Amply(
            """
            set elem;
            param init_stock{elem};
            param cost{elem};
            param value{elem};
            param : elem : init_stock  cost    value :=
            iron    7           25      1
            nickel  35          3       2
            ;
            """
        )
        s = result["init_stock"]
        assert s == {"iron": 7, "nickel": 35}
        assert result["cost"] == {"iron": 25, "nickel": 3}
        assert result["value"] == {"iron": 1, "nickel": 2}

    def test_set2_tabbing(self):
        result = amply.Amply(
            """
            set elem dimen 2;
            set elem := 0 0 1 1 2 2;
            param cost{elem};
            param value{elem};
            param : cost value :=
            0 0     7   25
            1 1     35  3
            ;
            """
        )

        assert result["elem"] == [(0, 0), (1, 1), (2, 2)]

    def test_undefined_tabbing_param(self):
        a = """
            param cost{elem};
            param : cost value :=
            0       1   2
            3       4   5
            ;
            """
        self.assertRaises(amply.AmplyError, lambda: amply.Amply(a))

    def test_2dset_simpleparam(self):
        result = amply.Amply(
            """
            set elem dimen 2;
            param foo{elem};
            param foo :=
                1   2   3
                2   3   4
                3   4   5
            ;
            """
        )["foo"]

        f = result[1][2]
        assert f == 3
        assert result[2][3] == 4
        assert result[3][4] == 5

    def test_tuple_param(self):
        result = amply.Amply(
            """
            set elem dimen 2;
            param foo{elem};
            param foo :=
                1   2   3
                2   3   4
                3   4   5
            ;
            """
        )["foo"]

        f = result[1, 2]
        assert f == 3
        assert result[2, 3] == 4
        assert result[3, 4] == 5

    def test_comment(self):
        result = amply.Amply(
            """
            # a comment
            set elem dimen 2;
            param foo{elem};
            param foo :=
                1   2   3
                2   3   4
                3   4   5
            ;
            """
        )["foo"]

        f = result[1, 2]
        assert f == 3
        assert result[2, 3] == 4
        assert result[3, 4] == 5

    def test_empty_tabbing_parameter_statement(self):

        result = amply.Amply(
            """
            set x;
            param square {x};
            param default 99 : square :=
            ;
            """
        )
        assert "square" in result.symbols.keys()
        assert result.square == {}

    def test_empty_tabbing_parameters(self):

        result = amply.Amply(
            """
            set x;
            param square {x};
            param triangle {x};
            param default 99 : square triangle :=
            ;
            """
        )
        assert "square" in result.symbols.keys()
        assert result.square == {}

    def test_empty_parameter_statement(self):
        result = amply.Amply(
            """
            param square {x};
            param square default 99 :=
            ;
            """
        )
        assert "square" in result.symbols.keys()
        assert result.square == {}

    def test_high_dim_tabbing(self):
        result = amply.Amply(
            """
            set x;
            set y;
            param square {x,y};
            param default 99 : square :=
            a a 34
            a b 35
            a c 36
            b a 53
            b b 45.3
            b c 459.2
            ;
            """
        )
        assert "square" in result.symbols.keys()
        print(result.square["b"])
        assert result.square["a"] == {"a": 34.0, "b": 35.0, "c": 36.0}
        assert result.square["b"] == {"a": 53.0, "b": 45.3, "c": 459.2}


if __name__ == "__main__":
    unittest.main()
