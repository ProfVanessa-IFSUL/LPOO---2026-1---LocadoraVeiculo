# LPOO - 2026-1 - Locadora de Veículos

Este é o projeto base utilizado na disciplina de **Linguagem de Programação Orientada a Objetos (LPOO)** do curso de Ciência da Computação, semestre **2026-1**, ministrada pela **Professora Vanessa**.

O objetivo deste projeto é servir como base prática para a aplicação de conceitos de Orientação a Objetos e Padrões de Projeto (Design Patterns) estudados em sala de aula.

## Tutoriais

Os guias práticos para a implementação dos padrões de projeto no sistema da locadora estão disponíveis na pasta `tutoriais/`:

*   [Aula 2 - Factory Method](<tutoriais/aula-2-tutorial--factory--locadora-veiculos.md>)
*   [Aula 3.1 - Strategy](<tutoriais/aula-3-1-tutorial-strategy--locadora-veiculos.md>)
*   [Aula 3.2 - State](<tutoriais/aula-3-2-tutorial-state--locadora-veiculos.md>)
*   [Aula 3.3 - Decorator](<tutoriais/aula-3-3-tutorial-decorator--locadora-veiculos.md>)

---

## Sobre o Projeto

O objetivo deste projeto é servir como base prática para a aplicação de conceitos de **Orientação a Objetos** e **Padrões de Projeto** (Design Patterns) estudados em sala de aula, evoluindo de forma incremental a cada aula/atividade.

O sistema simula uma **Locadora de Veículos** com as seguintes funcionalidades:

- **CRUD de Veículos** — cadastro, edição, remoção e visualização de veículos (Carro, Motorhome)
- **CRUD de Locações (Admin)** — gerenciamento completo de locações sem restrições de negócio
- **Operações de Locação (Usuário)** — reservar, locar, devolver e cancelar locações com regras de negócio
- **Validação de Disponibilidade** — filtro dinâmico de veículos disponíveis por período e categoria
- **Cálculo automático de valor** — cálculo de diárias na devolução usando Strategy Pattern


## Padrões de Projeto Utilizados

| Padrão | Onde é aplicado | Finalidade |
|--------|----------------|------------|
| **MVC** | Toda a aplicação | Separação de responsabilidades (Model, View, Controller) |
| **Factory** | `VeiculoFactory` | Criação de objetos Carro/Motorhome sem expor a lógica |
| **Strategy** | `CalculoPadraoStrategy` / `CalculoVIPStrategy` | Variação do algoritmo de cálculo de diárias |
| **State** | `estados_veiculo.py` / `estados_locacao.py` | Controle de estados de Veículos e Locações |
| **Decorator** | `decoradores.py` | Adição dinâmica de serviços extras à locação |
| **DAO** | `VeiculoDAO` / `LocacaoDAO` | Abstração da persistência em banco de dados |

---

## Banco de Dados

- **SGBD:** PostgreSQL
- **Banco:** `db_lpoo_locadora_veiculos`
- **Tabelas:**
  - `tb_veiculos` — cadastro de veículos (`vei_id` PK, `vei_placa` UNIQUE)
  - `tb_locacoes` — locações (`loc_id` PK, `loc_veiculo_id` FK → `vei_id`)
- **Script SQL:** [`sql/criar_tabela_locacoes.sql`](sql/criar_tabela_locacoes.sql)

### Modelo de Relacionamento

```
tb_veiculos (1) ──────── (N) tb_locacoes
     │                           │
  vei_id (PK) ◄─────FK───── loc_veiculo_id
```

### Script SQL

```sql
-- 1. Adicionar coluna de ID auto-increment em tb_veiculos (se não existir)
ALTER TABLE tb_veiculos 
  ADD COLUMN IF NOT EXISTS vei_id SERIAL;

-- 2. Garantir que vei_id seja PRIMARY KEY
ALTER TABLE tb_veiculos 
  DROP CONSTRAINT IF EXISTS tb_veiculos_pkey;
ALTER TABLE tb_veiculos 
  ADD CONSTRAINT tb_veiculos_pkey PRIMARY KEY (vei_id);
ALTER TABLE tb_veiculos 
  ADD CONSTRAINT tb_veiculos_placa_unique UNIQUE (vei_placa);

-- 3. Criar a tabela de Locações
CREATE TABLE IF NOT EXISTS tb_locacoes (
    loc_id            SERIAL        PRIMARY KEY,
    loc_veiculo_id    INTEGER       NOT NULL,
    loc_data_inicio   DATE          NOT NULL,
    loc_data_fim      DATE,
    loc_status        VARCHAR(20)   NOT NULL DEFAULT 'reservado'
                      CHECK (loc_status IN ('reservado', 'locado', 'devolvida', 'cancelada')),
    loc_valor_total   NUMERIC(10,2),
    loc_estrategia    VARCHAR(30)   NOT NULL DEFAULT 'padrao',
    CONSTRAINT fk_locacao_veiculo
        FOREIGN KEY (loc_veiculo_id)
        REFERENCES tb_veiculos (vei_id)
        ON DELETE RESTRICT
);

-- 4. Índices para otimizar consultas frequentes
CREATE INDEX IF NOT EXISTS idx_locacoes_status ON tb_locacoes (loc_status);
CREATE INDEX IF NOT EXISTS idx_locacoes_veiculo ON tb_locacoes (loc_veiculo_id);
```

---

## Itens de Aprendizado Esperados

Ao concluir este projeto, espera-se que o aluno tenha desenvolvido competência nos seguintes temas:

### Orientação a Objetos
- Encapsulamento (properties, getters/setters)
- Herança e Polimorfismo (VeiculoState → subclasses concretas)
- Classes abstratas (ABC, @abstractmethod)
- Composição de objetos (Locação possui Veiculo, Strategy e State)

### Padrões de Projeto (GoF)
- **Factory Method** — criação de objetos sem expor a lógica de instanciação
- **Strategy** — variação de algoritmos em tempo de execução (cálculo de diárias)
- **State** — comportamento variável conforme o estado do objeto (status da locação)
- **Decorator** — adição dinâmica de responsabilidades (serviços extras)

### Arquitetura e Persistência
- Padrão **MVC** — separação entre Model, View e Controller
- Padrão **DAO** — abstração do acesso a dados com `GenericDAO`
- Conexão e operações com **PostgreSQL** via `psycopg2`
- Modelagem relacional (chaves primárias, estrangeiras, constraints, índices)

### Interface Gráfica
- Tkinter: `tk.Tk`, `tk.Toplevel`, `tk.Menu`, `ttk.Treeview`, `ttk.Combobox`
- Hierarquia de janelas e fluxo `wait_window()`
- Validação de dados na interface e tratamento de erros com `messagebox`

### Boas Práticas
- Organização em pacotes (model, view, control, dao)
- Tratamento de exceções personalizadas
- Transparência no uso de ferramentas de IA

---

## 🤖 Declaração de Uso de IA

_(Prática comum de transparência acadêmica e profissional no GitHub)_

- [x] **Utilizei IA** como ferramenta de apoio.
  - **Ferramenta(s):** Gemini 3.1 Pro
  - **Finalidade:** Geração de boilerplate das Views Tkinter.
  - **Validação:** Todo o código gerado foi revisado, testado e ajustado conforme as necessidades específicas do projeto e da disciplina. A responsabilidade pela arquitetura, decisões de design e correção do código é da professora.

---

*Projeto desenvolvido para a disciplina LPOO — IFSul — Ciência da Computação — 2026/1*
*Professora Vanessa Lago Machado*
