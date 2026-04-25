import numpy as np
import pandas as pd


def simular_conversao_funil(porte: str) -> tuple[float, float]:
    """Sorteia taxas de conversão baseadas no porte do expositor."""
    if porte == "Pequeno":
        return np.random.uniform(0.15, 0.25), np.random.uniform(0.05, 0.10)
    elif porte == "Medio":
        return np.random.uniform(0.10, 0.18), np.random.uniform(0.03, 0.07)
    else:  # Grande
        return np.random.uniform(0.05, 0.12), np.random.uniform(0.01, 0.04)


def rodar_monte_carlo(
    yhat: float,
    porte: str,
    ticket_medio: float,
    percentual_comissao: float,
    minimo_garantido: float,
    volume_por_ponto: int = 100_000,
    n_simulacoes: int = 2000,
    seed: int = 42,
) -> dict:
    """
    Simulação Monte Carlo do modelo de comissão.

    Modelo:
        threshold = minimo_garantido / percentual_comissao + minimo_garantido

        - receita <= threshold → empresa recebe só o minimo_garantido
        - receita >  threshold → empresa recebe receita - threshold

    prob_vale_a_pena_pct = % de simulações onde o expositor superou o threshold.

    volume_vendas: derivado da mediana das receitas simuladas, revertendo o
    ticket_medio — representativo da distribuição real usada nas simulações,
    sem consumir o gerador aleatório após a seed principal.
    """
    np.random.seed(seed)

    receitas = np.array([
        (lambda t: yhat * volume_por_ponto * t[0] * t[1] * ticket_medio)(
            simular_conversao_funil(porte)
        )
        for _ in range(n_simulacoes)
    ])

    threshold = (
        (minimo_garantido / percentual_comissao) + minimo_garantido
        if percentual_comissao > 0
        else np.inf
    )

    receita_mediana = float(np.percentile(receitas, 50))

    ganho = minimo_garantido + max(0, receita_mediana - threshold)

    prob = (receitas > threshold).mean() * 100

    volume_vendas = int(round(receita_mediana / ticket_medio, 0)) if ticket_medio > 0 else 0

    if prob >= 60:
        status = "Comissão Vale A Pena"
    elif prob >= 40:
        status = "Risco Médio"
    else:
        status = "Comissão Não Vale A Pena"

    return {
        "prob_vale_a_pena_pct": round(prob, 2),
        "status_decisao":       status,
        "receita_mediana":      round(receita_mediana, 2),
        "ganho_medio":          round(ganho, 2),
        "threshold":            round(threshold, 2),
        "volume_vendas":        volume_vendas,
        "_receitas_dist":       receitas,
    }


def melhores_parametros_otimizados(resultado: pd.DataFrame, n_simulacoes: int = 2000):
    """
    Retorna uma lista de dicts com o melhor (comissão, MG) por faixa de
    probabilidade: 60-69%, 70-79%, 80-89%, 90-99%, 100%.
    Se nenhuma combinação atingir 60%, retorna uma única linha com o melhor encontrado.

    Cada dict contém:
        prob_alvo        (str)   — ex: "60%", "70%", "100%"
        prob_real        (float) — probabilidade real daquela combinação
        comissao         (str)   — ex: "45.0%"
        mg               (str)   — ex: "R$ 8.500,00"
        receita_empresa  (str)   — ex: "R$ 4.200,00"
        recomendado      (bool)  — True na primeira linha que bate 60%

    Mais os campos de contexto geral:
        nome_fantasia, status_atual, prob_atual, meta_teto_para_60pct,
        tem_otimizacao, tem_tabela, volume_vendas_base
    """

    # ------------------------------------------------------------------
    # 1. Guarda
    # ------------------------------------------------------------------
    df_ruins = resultado[
        resultado["status_decisao"] != "Comissão Vale A Pena"
    ].copy()

    if df_ruins.empty:
        return {}

    # ------------------------------------------------------------------
    # 2. Extrai variáveis
    # ------------------------------------------------------------------
    nome   = resultado["nome_fantasia"].iloc[0]
    yhat   = resultado["yhat_trends"].iloc[0]
    porte  = resultado["porte"].iloc[0]
    ticket = resultado["ticket_medio"].iloc[0]

    # ------------------------------------------------------------------
    # 3. Monte Carlo — seed isolada, gerador não reutilizado depois
    # ------------------------------------------------------------------
    np.random.seed(27)
    receitas_arr = np.array([
        yhat * 100_000
        * simular_conversao_funil(porte)[0]
        * simular_conversao_funil(porte)[1]
        * ticket
        for _ in range(n_simulacoes)
    ])
    meta_60_pct = np.percentile(receitas_arr, 40)

    # Volume base: mediana das receitas simuladas revertida pelo ticket.
    # Consistente com rodar_monte_carlo e não depende de nova amostragem.
    volume_vendas_base = int(round(float(np.percentile(receitas_arr, 50)) / ticket, 0)) if ticket > 0 else 0

    # ------------------------------------------------------------------
    # 4. Grid search 2D vetorizado
    # ------------------------------------------------------------------
    comissoes = np.arange(0.01, 0.16, 0.01)
    mgs       = np.arange(5000, 35500, 500)

    faixas = {60: None, 70: None, 80: None, 90: None, 100: None}
    melhor_geral = {"prob": -np.inf, "comissao": np.nan, "mg": np.nan,
                    "threshold": np.nan, "receita": np.nan}

    for comissao_teste in comissoes:
        for mg_teste in mgs:
            threshold = (mg_teste / comissao_teste) + mg_teste
            if meta_60_pct <= threshold:
                continue

            mask            = receitas_arr > threshold
            prob            = mask.sum() / n_simulacoes * 100
            receita_empresa = mg_teste + (meta_60_pct - threshold)

            candidato = {"prob": prob, "comissao": comissao_teste,
                         "mg": mg_teste, "threshold": threshold,
                         "receita": receita_empresa}

            # atualiza melhor geral (desempate por receita)
            if prob > melhor_geral["prob"] or (
                prob == melhor_geral["prob"] and receita_empresa > melhor_geral["receita"]
            ):
                melhor_geral = candidato.copy()

            # atualiza melhor por faixa
            for faixa in [100, 90, 80, 70, 60]:
                limite_inf = faixa if faixa < 100 else 100
                limite_sup = faixa + 9.999 if faixa < 100 else 100.001

                if limite_inf <= prob <= limite_sup:
                    atual = faixas[faixa]
                    if atual is None or receita_empresa > atual["receita"]:
                        faixas[faixa] = candidato.copy()
                    break

    # ------------------------------------------------------------------
    # 5. Monta linhas da tabela
    # ------------------------------------------------------------------
    linhas = []
    recomendado_marcado = False

    for faixa in [60, 70, 80, 90, 100]:
        c = faixas[faixa]
        if c is None:
            continue

        recomendado = False
        if not recomendado_marcado and c["prob"] >= 60:
            recomendado = True
            recomendado_marcado = True

        linhas.append({
            "prob_alvo":       f"{faixa}%",
            "prob_real":       round(c["prob"], 1),
            "comissao":        f"{c['comissao']:.1%}",
            "mg":              f"R$ {c['mg']:,.2f}",
            "receita_empresa": f"R$ {c['receita']:,.2f}",
            "recomendado":     recomendado,
        })

    # Se nenhuma faixa >= 60% foi encontrada, mostra só o melhor geral
    tem_tabela = len(linhas) > 0
    if not tem_tabela and melhor_geral["prob"] != -np.inf:
        linhas.append({
            "prob_alvo":       "Melhor possível",
            "prob_real":       round(melhor_geral["prob"], 1),
            "comissao":        f"{melhor_geral['comissao']:.1%}",
            "mg":              f"R$ {melhor_geral['mg']:,.2f}",
            "receita_empresa": f"R$ {melhor_geral['receita']:,.2f}",
            "recomendado":     False,
        })

    return {
        "nome_fantasia":        nome,
        "status_atual":         resultado["status_decisao"].iloc[0],
        "prob_atual":           resultado["prob_vale_a_pena_pct"].iloc[0],
        "meta_teto_para_60pct": round(meta_60_pct, 2),
        "tem_otimizacao":       len(linhas) > 0,
        "tem_tabela":           tem_tabela,
        "linhas":               linhas,
        "volume_vendas_base":   volume_vendas_base,
    }