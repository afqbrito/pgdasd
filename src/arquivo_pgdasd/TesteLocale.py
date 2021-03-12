# -*- coding: utf-8 -*-

import locale


def body():
    suggestion = 3500
    str_value = input(
        "Digite a pretenção salarial (exemplo: R$ {}): ".format(
            locale.format_string("%.2f", suggestion)
        )
    )
    value = locale.atof(str_value)
    print(
        "Valor numérico interno: {}. Valor formatado: {}".format(value,
            locale.format_string("%.2f", value, grouping=True, monetary=True)
        )
    )


def main():
    for locale_name in ("pt_BR", "en_US"):
        locale.setlocale(locale.LC_ALL, locale_name)
        print("\n\nExemplo usando o locale {}: \n".format(locale_name))
        body()


if __name__ == "__main__":
    main()
    