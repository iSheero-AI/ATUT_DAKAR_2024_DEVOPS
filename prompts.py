def prompt(query: str, context: str):
    user_prompt = (
            """Essaie de répondre à la question dans un langage clair et simple en te basant le plus possible sur le contexte.

Si le *contexte* fourni ne contient pas la réponse à la question, n'essaie pas d'inventer une réponse, dis `Désolé, je ne trouve pas de réponse exacte`.

Procéde étape par étape pour être sûrs d'avoir la bonne réponse.

### CONTEXTE:
```
{context}
```

### QUESTION:
```
{question}
```

La réponse fournie doit être courte, informative et uniquement en Français.
Fais ressortir l'url (exemple:https://eservices.anip.bj) du service `qui se trouve dans le contexte` si il y en a.
Fais un focus sur les documents à fournir dans les détails, le coût, la durée.
N'oublie pas de faire ressortir toutes les conditions possibles pour répondre à cette question.
### RÉPONSE:
            """)
    
    return user_prompt