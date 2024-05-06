from db_interface import DBInterface
import pandas as pd


def projeto_carteira():
    db = DBInterface()
    query = """
    WITH ProjetosNumerados AS (
        SELECT *,
            ROW_NUMBER() OVER (PARTITION BY p.ProjetoId ORDER BY p.DtUltMM DESC) AS Num
        FROM Projeto p
    )
    SELECT p.ProjetoId,
        ppc.Carteira 'Carteira de Obras',
        p.VlProjeto 'Valor do Projeto',
        pct.Nome AS 'Programacao Carteira Tipo',
        ISNULL(BoltimProdutividade.Total_Instalado, 0) AS 'Total Instalado',
        Total_Poste.Soma_Prev as 'Total Previsto'
    FROM ProjetosNumerados p
    JOIN ProjetoProgramacaoCarteira ppc ON p.ProjetoId = ppc.ProjetoId
    JOIN ProjetoTipo pt ON p.ProjetoTipoId = pt.ProjetoTipoId
    JOIN StatusProjeto sp ON sp.StatusProjetoId = p.StatusProjetoId
    JOIN TipoInstalacao ti ON ti.TipoInstalacaoId = p.TipoInstalacaoId
    LEFT JOIN ProgramacaoCarteiraTipo pct ON pct.ProgramacaoCarteiraTipoId = ppc.ProgramacaoCarteiraTipoId
    LEFT JOIN (
        SELECT ProjetoId, SUM(ppbp.Instalado) AS Total_Instalado
        FROM ProjetoProgramacaoBoletimProdutividade ppbp
        GROUP BY ProjetoId
    ) BoltimProdutividade ON BoltimProdutividade.ProjetoId = p.ProjetoId
    LEFT JOIN (
        SELECT p.ProjetoId,
                    (PostePriPrev + PosteSecPrev) AS Soma_Prev
        FROM Projeto p
    ) Total_Poste ON Total_Poste.ProjetoId = p.ProjetoId
    WHERE YEAR(ppc.Carteira) BETWEEN YEAR(GETDATE()) AND YEAR(GETDATE()) + 1
    AND p.Num = 1
    ORDER BY ppc.Carteira ASC;
    """
    df = db.query(query, "projeto_carteira")
    df["Carteira de Obras"] = pd.to_datetime(df["Carteira de Obras"])
    db.close()
    return df


if __name__ == "__main__":
    df = projeto_carteira()
    print(df.head())
