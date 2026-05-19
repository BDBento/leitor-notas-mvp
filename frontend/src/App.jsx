import React, { useEffect, useState } from "react";
import { apiFetch, setToken, removeToken, getToken } from "./services/api";

const API_URL = "http://localhost:8000";

function App() {
  const [email, setEmail] = useState("");
  const [senha, setSenha] = useState("");
  const [gastos, setGastos] = useState([]);
  const [logado, setLogado] = useState(Boolean(getToken()));
  const [erro, setErro] = useState("");
  const [carregando, setCarregando] = useState(false);
  const [arquivo, setArquivo] = useState(null);

  async function login(e) {
    e.preventDefault();
    setErro("");

    try {
      const data = await apiFetch("/auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email,
          senha,
        }),
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

  function sair() {
    removeToken();
    setLogado(false);
    setGastos([]);
  }

  useEffect(() => {
    if (logado) {
      carregarGastos();
    }
  }, [logado]);

  const total = gastos.reduce((soma, gasto) => {
    return soma + Number(gasto.valor_total || 0);
  }, 0);

  if (!logado) {
    return (
      <main style={{ padding: 40, fontFamily: "Arial", maxWidth: 420 }}>
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
    <main style={{ padding: 40, fontFamily: "Arial" }}>
      <header style={{ display: "flex", justifyContent: "space-between" }}>
        <div>
          <h1>Dashboard de Gastos</h1>
          <p>Notas processadas pelo OCR</p>
        </div>

        <button onClick={sair} style={{ height: 40 }}>
          Sair
        </button>
      </header>

      {erro && <p style={{ color: "red" }}>{erro}</p>}

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
          <strong>{gastos.length}</strong>
        </div>
      </section>

      <section
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

      <section>
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
            </tr>
          </thead>

          <tbody>
            {gastos.map((gasto) => (
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
              </tr>
            ))}

            {gastos.length === 0 && (
              <tr>
                <td colSpan="7">Nenhum gasto encontrado.</td>
              </tr>
            )}
          </tbody>
        </table>
      </section>
    </main>
  );
}

export default App;