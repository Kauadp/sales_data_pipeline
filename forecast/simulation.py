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
        - receita >  threshold → empresa recebe minimo_garantido
                                 + (receita - threshold) * percentual_comissao

    prob_vale_a_pena_pct = % de simulações onde o expositor superou o threshold.
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

    ganhos = np.where(
        receitas > threshold,
        receitas - threshold,
        minimo_garantido,
    )

    prob = (receitas > threshold).mean() * 100

    if prob >= 60:
        status = "Comissão Vale A Pena"
    elif prob >= 40:
        status = "Risco Médio"
    else:
        status = "Comissão Não Vale A Pena"

    return {
        "prob_vale_a_pena_pct": round(prob, 2),
        "status_decisao":       status,
        "receita_mediana":      round(float(np.percentile(receitas, 50)), 2),
        "receita_p10":          round(float(np.percentile(receitas, 10)), 2),
        "receita_p90":          round(float(np.percentile(receitas, 90)), 2),
        "ganho_medio":          round(float(ganhos.mean()), 2),
        "threshold":            round(threshold, 2),
        "_receitas_dist":       receitas,
    }