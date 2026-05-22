import React, { useEffect, useState } from "react";
import { apiFetch, setToken, removeToken, getToken } from "./services/api";
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

import "./App.css";

const API_URL = "http://localhost:8000";

function App() {
  const [email, setEmail] = useState("");
  const [senha, setSenha] = useState("");
  const [gastos, setGastos] = useState([]);
  const [logado, setLogado] = useState(Boolean(getToken()));
  const [erro, setErro] = useState("");
  const [carregando, setCarregando] = useState(false);
  const [arquivo, setArquivo] = useState(null);
  const [mesSelecionado, setMesSelecionado] = useState("");

  const [editando, setEditando] = useState(null);
  const [formEdicao, setFormEdicao] = useState({
    data_gasto: "",
    estabelecimento: "",
    categoria: "",
    valor_total: "",
    forma_pagamento: "",
  });

  const [usuario, setUsuario] = useState(null);

  const [novaSenha, setNovaSenha] = useState("");
  const [mensagemSenha, setMensagemSenha] = useState("");

  async function login(e) {
    e.preventDefault();
    setErro("");

    try {
      const data = await apiFetch("/auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, senha }),
      });

      setToken(data.access_token);
      setLogado(true);
    } catch {
      setErro("E-mail ou senha inválidos.");
    }
  }

  async function carregarGastos() {
    try {
      const data = await apiFetch("/gastos/");
      setGastos(data);
    } catch {
      setErro("Erro ao carregar gastos.");
    }
  }

  async function carregarUsuario() {
    try {
      const data = await apiFetch("/auth/me");
      setUsuario(data);
    } catch {
      setErro("Erro ao carregar usuário.");
    }
  }

  async function alterarSenha(e) {
    e.preventDefault();

    setMensagemSenha("");

    try {
      await apiFetch("/usuarios/alterar-senha", {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          nova_senha: novaSenha,
        }),
      });

      setNovaSenha("");
      setMensagemSenha("Senha alterada com sucesso.");
    } catch {
      setMensagemSenha("Erro ao alterar senha.");
    }
  }

  async function enviarArquivo(e) {
    e.preventDefault();

    if (!arquivo) {
      setErro("Selecione uma imagem antes de enviar.");
      return;
    }

    setErro("");
    setCarregando(true);

    try {
      const formData = new FormData();
      formData.append("file", arquivo);

      await apiFetch("/upload/", {
        method: "POST",
        body: formData,
      });

      setArquivo(null);
      await carregarGastos();
    } catch (error) {
      setErro(error.message || "Erro ao enviar imagem.");
    } finally {
      setCarregando(false);
    }
  }

  function abrirEdicao(gasto) {
    setEditando(gasto.id);
    setFormEdicao({
      data_gasto: gasto.data_gasto || "",
      estabelecimento: gasto.estabelecimento || "",
      categoria: gasto.categoria || "",
      valor_total: gasto.valor_total || "",
      forma_pagamento: gasto.forma_pagamento || "",
    });
  }

  function cancelarEdicao() {
    setEditando(null);
    setFormEdicao({
      data_gasto: "",
      estabelecimento: "",
      categoria: "",
      valor_total: "",
      forma_pagamento: "",
    });
  }

  async function salvarEdicao(e) {
    e.preventDefault();
    setErro("");

    try {
      await apiFetch(`/gastos/${editando}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          data_gasto: formEdicao.data_gasto || null,
          estabelecimento: formEdicao.estabelecimento || null,
          categoria: formEdicao.categoria || null,
          valor_total: formEdicao.valor_total
            ? Number(formEdicao.valor_total)
            : null,
          forma_pagamento: formEdicao.forma_pagamento || null,
        }),
      });

      cancelarEdicao();
      await carregarGastos();
    } catch (error) {
      setErro(error.message || "Erro ao salvar edição.");
    }
  }

  async function excluirGasto(id) {
    const confirmar = window.confirm("Deseja realmente excluir este gasto?");

    if (!confirmar) return;

    try {
      await apiFetch(`/gastos/${id}`, {
        method: "DELETE",
      });

      await carregarGastos();
    } catch (error) {
      setErro(error.message || "Erro ao excluir gasto.");
    }
  }

  function exportarCSV() {
    if (gastosFiltrados.length === 0) {
      setErro("Não há dados para exportar.");
      return;
    }

    const cabecalho = [
      "ID",
      "Data",
      "Estabelecimento",
      "Categoria",
      "Valor",
      "Forma de pagamento",
      "Status",
    ];

    const linhas = gastosFiltrados.map((gasto) => [
      gasto.id,
      gasto.data_gasto || "",
      gasto.estabelecimento || "",
      gasto.categoria || "",
      gasto.valor_total || "",
      gasto.forma_pagamento || "",
      gasto.status_processamento || "",
    ]);

    const conteudoCSV = [cabecalho, ...linhas]
      .map((linha) =>
        linha
          .map((campo) => `"${String(campo).replaceAll('"', '""')}"`)
          .join(";"),
      )
      .join("\n");

    const blob = new Blob(["\uFEFF" + conteudoCSV], {
      type: "text/csv;charset=utf-8;",
    });

    const url = URL.createObjectURL(blob);

    const link = document.createElement("a");
    link.href = url;
    link.download = mesSelecionado
      ? `gastos-${mesSelecionado}.csv`
      : "gastos.csv";

    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    URL.revokeObjectURL(url);
  }

  function sair() {
    removeToken();
    setLogado(false);
    setGastos([]);
  }

  useEffect(() => {
    if (logado) {
      carregarGastos();
      carregarUsuario();
    }
  }, [logado]);

  const gastosFiltrados = gastos.filter((gasto) => {
    if (!mesSelecionado) {
      return true;
    }

    if (!gasto.data_gasto) {
      return false;
    }

    return gasto.data_gasto.startsWith(mesSelecionado);
  });

  const total = gastosFiltrados.reduce((soma, gasto) => {
    return soma + Number(gasto.valor_total || 0);
  }, 0);

  const categoriasAgrupadas = gastosFiltrados.reduce((acc, gasto) => {
    const categoria = gasto.categoria || "Outros";
    const valor = Number(gasto.valor_total || 0);

    if (!acc[categoria]) {
      acc[categoria] = 0;
    }

    acc[categoria] += valor;

    return acc;
  }, {});

  const rankingCategorias = Object.entries(categoriasAgrupadas)
    .map(([categoria, valor]) => ({
      categoria,
      valor,
    }))
    .sort((a, b) => b.valor - a.valor);

  const dadosGrafico = Object.entries(categoriasAgrupadas).map(
    ([name, value]) => ({
      name,
      value,
    }),
  );

  const COLORS = [
    "#0088FE",
    "#00C49F",
    "#FFBB28",
    "#FF8042",
    "#A020F0",
    "#FF4560",
  ];

  if (!logado) {
    return (
      <main className="login-page">
        <h1>Leitor de Notas</h1>
        <h2>Login</h2>

        <form onSubmit={login}>
          <div style={{ marginBottom: 12 }}>
            <label>E-mail</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              style={{ width: "100%", padding: 10, marginTop: 4 }}
              required
            />
          </div>

          <div style={{ marginBottom: 12 }}>
            <label>Senha</label>
            <input
              type="password"
              value={senha}
              onChange={(e) => setSenha(e.target.value)}
              style={{ width: "100%", padding: 10, marginTop: 4 }}
              required
            />
          </div>

          {erro && <p style={{ color: "red" }}>{erro}</p>}

          <button type="submit" style={{ padding: "10px 18px" }}>
            Entrar
          </button>
        </form>
      </main>
    );
  }

  return (
    <div className="dashboard-layout">
      <aside className="sidebar">
        <div className="sidebar-logo">
          <strong>Leitor de Notas</strong>
          <span>MVP Financeiro</span>
        </div>

        <nav className="sidebar-nav">
          <a href="#dashboard">Dashboard</a>
          <a href="#upload">Upload</a>
          <a href="#analytics">Analytics</a>
          <a href="#gastos">Gastos</a>
          <a href="#configuracoes">Configurações</a>
        </nav>
      </aside>

      <main className="app-shell">
        <header
          id="dashboard"
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            marginBottom: 30,
            padding: 20,
            border: "1px solid #ddd",
            borderRadius: 8,
          }}
        >
          <div>
            <h1 style={{ margin: 0 }}>Dashboard de Gastos</h1>

            <p style={{ marginTop: 8 }}>
              Usuário:
              <strong> {usuario?.nome || "Carregando..."}</strong>
            </p>

            <p style={{ marginTop: 4 }}>{usuario?.email}</p>
          </div>

          <button onClick={sair} style={{ height: 40 }}>
            Sair
          </button>
        </header>

        {erro && <p style={{ color: "red" }}>{erro}</p>}

        <section
          id="configuracoes"
          style={{
            border: "1px solid #ddd",
            borderRadius: 8,
            padding: 20,
            marginBottom: 30,
          }}
        >
          <h2>Alterar senha</h2>

          <form onSubmit={alterarSenha}>
            <input
              type="password"
              placeholder="Nova senha"
              value={novaSenha}
              onChange={(e) => setNovaSenha(e.target.value)}
              style={{
                padding: 10,
                marginRight: 10,
                width: 240,
              }}
            />

            <button type="submit">Atualizar senha</button>
          </form>

          {mensagemSenha && <p style={{ marginTop: 10 }}>{mensagemSenha}</p>}
        </section>

        <section
          style={{
            border: "1px solid #ddd",
            borderRadius: 8,
            padding: 20,
            marginBottom: 30,
          }}
        >
          <h2>Filtro mensal</h2>

          <input
            type="month"
            value={mesSelecionado}
            onChange={(e) => setMesSelecionado(e.target.value)}
            style={{
              padding: 10,
              marginRight: 10,
            }}
          />

          <button
            type="button"
            onClick={() => setMesSelecionado("")}
            style={{
              padding: "10px 16px",
            }}
          >
            Limpar filtro
          </button>

          <button
            type="button"
            onClick={exportarCSV}
            style={{
              padding: "10px 16px",
              marginLeft: 10,
            }}
          >
            Exportar CSV
          </button>
        </section>

        <section
          style={{
            display: "flex",
            gap: 20,
            marginTop: 30,
            marginBottom: 30,
          }}
        >
          <div
            style={{
              border: "1px solid #ddd",
              padding: 20,
              borderRadius: 8,
              minWidth: 220,
            }}
          >
            <h3>Total registrado</h3>
            <strong>R$ {total.toFixed(2)}</strong>
          </div>

          <div
            style={{
              border: "1px solid #ddd",
              padding: 20,
              borderRadius: 8,
              minWidth: 220,
            }}
          >
            <h3>Notas enviadas</h3>
            <strong>{gastosFiltrados.length}</strong>
          </div>
        </section>

        <section
          id="upload"
          style={{
            border: "1px solid #ddd",
            padding: 20,
            borderRadius: 8,
            marginBottom: 30,
          }}
        >
          <h2>Enviar nova nota</h2>

          <form onSubmit={enviarArquivo}>
            <input
              type="file"
              accept=".jpg,.jpeg,.png,.pdf"
              onChange={(e) => setArquivo(e.target.files[0])}
            />

            <button
              type="submit"
              disabled={carregando}
              style={{ marginLeft: 12, padding: "8px 16px" }}
            >
              {carregando ? "Processando..." : "Enviar"}
            </button>
          </form>
        </section>

        {editando && (
          <section
            style={{
              border: "1px solid #ccc",
              padding: 20,
              borderRadius: 8,
              marginBottom: 30,
            }}
          >
            <h2>Editando gasto #{editando}</h2>

            <form onSubmit={salvarEdicao}>
              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "repeat(2, 1fr)",
                  gap: 12,
                }}
              >
                <div>
                  <label>Data</label>
                  <input
                    type="date"
                    value={formEdicao.data_gasto}
                    onChange={(e) =>
                      setFormEdicao({
                        ...formEdicao,
                        data_gasto: e.target.value,
                      })
                    }
                    style={{ width: "100%", padding: 8 }}
                  />
                </div>

                <div>
                  <label>Valor</label>
                  <input
                    type="number"
                    step="0.01"
                    value={formEdicao.valor_total}
                    onChange={(e) =>
                      setFormEdicao({
                        ...formEdicao,
                        valor_total: e.target.value,
                      })
                    }
                    style={{ width: "100%", padding: 8 }}
                  />
                </div>

                <div>
                  <label>Estabelecimento</label>
                  <input
                    type="text"
                    value={formEdicao.estabelecimento}
                    onChange={(e) =>
                      setFormEdicao({
                        ...formEdicao,
                        estabelecimento: e.target.value,
                      })
                    }
                    style={{ width: "100%", padding: 8 }}
                  />
                </div>

                <div>
                  <label>Categoria</label>
                  <input
                    type="text"
                    value={formEdicao.categoria}
                    onChange={(e) =>
                      setFormEdicao({
                        ...formEdicao,
                        categoria: e.target.value,
                      })
                    }
                    style={{ width: "100%", padding: 8 }}
                  />
                </div>

                <div>
                  <label>Forma de pagamento</label>
                  <input
                    type="text"
                    value={formEdicao.forma_pagamento}
                    onChange={(e) =>
                      setFormEdicao({
                        ...formEdicao,
                        forma_pagamento: e.target.value,
                      })
                    }
                    style={{ width: "100%", padding: 8 }}
                  />
                </div>
              </div>

              <div style={{ marginTop: 16 }}>
                <button type="submit" style={{ padding: "8px 16px" }}>
                  Salvar
                </button>

                <button
                  type="button"
                  onClick={cancelarEdicao}
                  style={{ padding: "8px 16px", marginLeft: 8 }}
                >
                  Cancelar
                </button>
              </div>
            </form>
          </section>
        )}

        <section
          id="analytics"
          style={{
            border: "1px solid #ddd",
            borderRadius: 8,
            padding: 20,
            marginBottom: 30,
          }}
        >
          <h2>Gastos por categoria</h2>

          {dadosGrafico.length > 0 ? (
            <div style={{ width: "100%", height: 350 }}>
              <ResponsiveContainer>
                <PieChart>
                  <Pie
                    data={dadosGrafico}
                    dataKey="value"
                    nameKey="name"
                    outerRadius={120}
                    label
                  >
                    {dadosGrafico.map((entry, index) => (
                      <Cell
                        key={`cell-${index}`}
                        fill={COLORS[index % COLORS.length]}
                      />
                    ))}
                  </Pie>

                  <Tooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <p>Nenhum dado disponível para o gráfico.</p>
          )}
        </section>

        <section
          id="analytics"
          style={{
            border: "1px solid #ddd",
            borderRadius: 8,
            padding: 20,
            marginBottom: 30,
          }}
        >
          <h2>Analytics financeiros</h2>

          {rankingCategorias.length === 0 ? (
            <p>Nenhum dado disponível.</p>
          ) : (
            <table
              width="100%"
              border="1"
              cellPadding="10"
              style={{
                borderCollapse: "collapse",
                marginTop: 20,
              }}
            >
              <thead>
                <tr>
                  <th>Posição</th>
                  <th>Categoria</th>
                  <th>Total</th>
                </tr>
              </thead>

              <tbody>
                {rankingCategorias.map((item, index) => (
                  <tr key={item.categoria}>
                    <td>#{index + 1}</td>

                    <td>{item.categoria}</td>

                    <td>R$ {Number(item.valor).toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </section>

        <section id="gastos">
          <h2>Gastos cadastrados</h2>

          <table
            border="1"
            cellPadding="10"
            style={{ borderCollapse: "collapse", width: "100%" }}
          >
            <thead>
              <tr>
                <th>ID</th>
                <th>Data</th>
                <th>Estabelecimento</th>
                <th>Categoria</th>
                <th>Valor</th>
                <th>Status</th>
                <th>Imagem</th>
                <th>Ações</th>
              </tr>
            </thead>

            <tbody>
              {gastosFiltrados.map((gasto) => (
                <tr key={gasto.id}>
                  <td>{gasto.id}</td>
                  <td>{gasto.data_gasto || "-"}</td>
                  <td>{gasto.estabelecimento || "-"}</td>
                  <td>{gasto.categoria || "-"}</td>
                  <td>
                    {gasto.valor_total
                      ? `R$ ${Number(gasto.valor_total).toFixed(2)}`
                      : "-"}
                  </td>
                  <td>{gasto.status_processamento}</td>
                  <td>
                    {gasto.imagem_url ? (
                      <a
                        href={`${API_URL}${gasto.imagem_url}`}
                        target="_blank"
                        rel="noreferrer"
                      >
                        Ver imagem
                      </a>
                    ) : (
                      "-"
                    )}
                  </td>
                  <td>
                    <button onClick={() => abrirEdicao(gasto)}>Editar</button>
                    <button
                      onClick={() => excluirGasto(gasto.id)}
                      style={{ marginLeft: 8 }}
                    >
                      Excluir
                    </button>
                  </td>
                </tr>
              ))}

              {gastosFiltrados.length === 0 && (
                <tr>
                  <td colSpan="8">Nenhum gasto encontrado.</td>
                </tr>
              )}
            </tbody>
          </table>
        </section>
      </main>
    </div>
  );
}

export default App;
