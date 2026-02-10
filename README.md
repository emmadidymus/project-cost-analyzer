# Engineering Project Cost & Risk Analyzer

A professional web application for estimating project costs, timelines, and analyzing risks using Monte Carlo simulation. Built with Python, Streamlit, and advanced project management algorithms.

🔗 **[Live Demo](https://project-cost-analyzer.streamlit.app/)**

---

## 🎯 Features

### Core Functionality
- **📊 Cost Estimation**: Calculate base costs and risk-adjusted project estimates
- **⏱️ Timeline Analysis**: Multiple timeline scenarios (sequential, optimistic, realistic)
- **🔗 Dependency Management**: Critical path analysis with task dependencies
- **👥 Resource Allocation**: Model team capacity and resource constraints
- **🎲 Monte Carlo Simulation**: Run 100-5000+ scenarios to quantify uncertainty
- **📈 Professional Visualizations**: Interactive charts and distribution analysis
- **📑 Export Reports**: Download analysis as CSV with detailed breakdowns

### Technical Highlights
- **Critical Path Algorithm**: Identifies bottlenecks using topological sorting
- **Resource-Constrained Scheduling**: Simulates realistic project timelines
- **Statistical Analysis**: Percentile calculations, variance analysis, risk drivers
- **Interactive Web UI**: Built with Streamlit for seamless user experience

---

## 🚀 Quick Start

### **Option 1: Use the Live App (Recommended)**
Visit the [live demo](https://project-cost-analyzer.streamlit.app/) - no installation required!

### **Option 2: Run Locally**

**Prerequisites:**
- Python 3.9 or higher
- pip package manager

**Installation:**
```bash
# Clone the repository
git clone https://github.com/emmadidymus/project-cost-analyzer.git
cd project-cost-analyzer

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the web app
python -m streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

---

## 📖 Usage Guide

### 1️⃣ **Configure Your Project**
- Enter project name, team size, and risk level (low/medium/high)

### 2️⃣ **Add Tasks**
- Define tasks with estimated duration and daily cost
- Set dependencies to model task relationships
- Tasks are automatically validated for circular dependencies

### 3️⃣ **View Analysis**
- **Overview Tab**: See instant cost and timeline estimates
- **Analysis Tab**: Detailed breakdown with critical path
- **Monte Carlo Tab**: Run risk simulations (1000+ iterations)
- **Charts Tab**: Generate and download professional visualizations

### 4️⃣ **Export Results**
- Download CSV reports with complete analysis
- Save visualization charts (PNG format)
- Share results with stakeholders

---

## 🏗️ Project Structure
```
project_cost_analyzer/
├── app.py                  # Streamlit web interface
├── main.py                 # CLI version (alternative interface)
├── src/
│   ├── project.py          # Project and Task data models
│   ├── calculator.py       # Cost and timeline calculations
│   ├── risk_simulator.py   # Monte Carlo simulation engine
│   ├── visualizer.py       # Chart generation (Matplotlib)
│   └── utils.py            # Helper functions
├── tests/
│   └── test_calculator.py  # Unit tests (pytest)
├── output/reports/         # Generated reports and charts
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

---

## 🧪 Testing

Run the test suite:
```bash
pytest tests/ -v
```

**Test Coverage:**
- ✅ Cost calculations (base, risk-adjusted, per-resource)
- ✅ Timeline estimation (sequential, parallel, resource-constrained)
- ✅ Critical path analysis
- ✅ Dependency validation (including circular detection)
- ✅ Edge cases (single task, empty projects, invalid inputs)

---

## 🛠️ Technologies Used

### Core
- **Python 3.13** - Primary language
- **Streamlit** - Web framework
- **NumPy** - Numerical computations
- **Pandas** - Data manipulation

### Visualization
- **Matplotlib** - Static charts (PNG export)
- **Plotly** - Interactive histograms

### Testing & Quality
- **Pytest** - Unit testing framework
- **Type hints** - Code documentation and IDE support

---

## 📊 Example Use Cases

1. **Software Development Projects**
   - Estimate sprint timelines with team constraints
   - Model risk of feature delays
   - Optimize resource allocation

2. **Infrastructure Projects**
   - Calculate construction costs with material uncertainty
   - Identify critical path for project milestones
   - Scenario planning for budget overruns

3. **Product Launches**
   - Timeline estimation with marketing dependencies
   - Cost modeling for multi-phase rollouts
   - Risk analysis for go-to-market strategies

---

## 🎓 Key Algorithms

### Critical Path Method (CPM)
Uses topological sorting to identify the longest dependent chain of tasks - the minimum project duration.

### Monte Carlo Simulation
Runs 1000+ iterations with randomized:
- Task duration variations (based on risk level)
- Cost fluctuations (±15-50% depending on risk)
- Resource contention delays
- Random risk factors (normally distributed)

### Resource-Constrained Scheduling
Simulates realistic timelines considering:
- Limited team availability
- Task dependencies
- Parallel work capacity
- Queuing delays

---

## 📈 Future Enhancements

- [ ] Machine learning for better cost predictions
- [ ] Integration with project management tools (Jira, Asana)
- [ ] Team skill level modeling
- [ ] Historical project data import
- [ ] Multi-currency support
- [ ] Gantt chart visualization
- [ ] PDF report generation

---

## 🤝 Contributing

This is a portfolio project, but suggestions are welcome!

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

---

## 👨‍💻 About

Created as a portfolio project demonstrating:
- Systems thinking and engineering management principles
- Python software architecture and best practices
- Statistical modeling and risk analysis
- Production-ready code with testing
- Professional web application development

**Perfect for:** MS Engineering Management applications, technical project manager roles, or data-driven decision-making portfolios.

---

## 📧 Contact

Emmanuel Didymus Sebastian - emmanueldidymus@gmail.com

Project Link: [https://github.com/emmadidymus/project-cost-analyzer](https://github.com/emmadidymus/project-cost-analyzer)

---

## 🙏 Acknowledgments

- Monte Carlo simulation methodology inspired by industry-standard risk analysis
- Critical Path Method based on project management literature
- Built with modern Python best practices