import ply.lex as plex

# Classe LogicLexer
class LogicLexer:

    keywords = ()
    
    # Tokens
    tokens = ("var", "atribui", "nr", "string", "verdadeiro", "falso", "nao", "e", "ou", "escrever",
              "entrada", "Inicio", "Fim", "cos", "sen", "se", "fim_se", "entao", "senao", "para", "de",
              "ate", "fim_para", "fun", "STRING", "aleatorio", "fazer", "chamada_funcao")

    #Literals
    literals = ['(', ')', '+', '-', '/', '*', ';', '[', ']', '#', ':', '>', '<', '=']

    #Ignorar espaços em branco, tabs e quebras de linha
    t_ignore = " \t\n"

    def __init__(self):
        self.lex = None

    def t_comment(self, t):
        r"""\#.*"""
        t.value = t.value[1:]
        if '\n' not in t.value:
            t.type = 'comment_single'
            t.value = f"//{t.value}"
        else:
            t.type = 'comment_multi'
            t.value = f"/*{t.value}*/"
        return t

    def t_string(self, t):
        r'"[^"]*"'
        t.value = t.value[1:-1]
        return t

    def t_str(self, t):
        r"nao|verdadeiro|falso|e(screver)?|ou|para|Inicio|Fim|cos|atribui|sen|inteiro|se|fun|entrada|fazer"
        t.type = t.value
        return t

    def t_var(self, t):
        r"[a-z_]+"
        return t

    def t_nr(self, t):
        r"""[0-9]+(\.[0-9]+)?"""
        t.value = float(t.value)
        return t

    def t_aleatorio(self, t):
        r"""aleatorio"""
        return t

    def t_chamada_funcao(self, t):
        r"[a-z_]+\s*\("
        t.value = t.value.strip()[:-1]  # Remove the opening parenthesis
        t.type = "chamada_funcao"
        return t

    def build(self, **kwargs):
        self.lex = plex.lex(module=self, **kwargs)

    def token(self):
        token = self.lex.token()
        return token if token is None else token.type

    def t_error(self, t):
        raise Exception(f"Unexpected token {t.value[:10]}")
