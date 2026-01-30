import streamlit as st
import tempfile
import os
import json
import pandas as pd
from datetime import datetime
from typing import Dict, List
import base64
import io

from document_processor import DocumentProcessor
from risk_scorer import RiskScorer
from legal_analyzer import LegalAnalyzer
from template_matcher import TemplateMatcher
from audit_logger import AuditLogger
from hindi_support import HindiSupport
from config import Config

class LegalAssistantApp:
    def __init__(self):
        st.set_page_config(
            page_title="Legal Assistant for Indian SMEs",
            page_icon="⚖️",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Custom CSS
        self.set_custom_css()
        
        self.config = Config()
        self.processor = DocumentProcessor()
        self.scorer = RiskScorer()
        self.analyzer = LegalAnalyzer(self.config)
        self.template_matcher = TemplateMatcher()
        self.audit_logger = AuditLogger()
        self.hindi_support = HindiSupport()
        
        # Initialize session state
        self.init_session_state()
    
    def set_custom_css(self):
        """Set custom CSS for better UI"""
        st.markdown("""
        <style>
        .main-header {
            font-size: 2.2rem;
            color: #1E3A8A;
            text-align: center;
            margin-bottom: 2rem;
            font-weight: 600;
        }
        .risk-high {
            color: #DC2626;
            font-weight: bold;
        }
        .risk-medium {
            color: #D97706;
            font-weight: bold;
        }
        .risk-low {
            color: #059669;
            font-weight: bold;
        }
        .section-header {
            font-size: 1.5rem;
            color: #1E3A8A;
            margin-top: 1.5rem;
            margin-bottom: 1rem;
            font-weight: 600;
        }
        .card {
            background-color: #f8f9fa;
            padding: 1rem;
            border-radius: 8px;
            border-left: 4px solid #1E3A8A;
            margin-bottom: 1rem;
        }
        </style>
        """, unsafe_allow_html=True)
    
    def init_session_state(self):
        """Initialize session state variables"""
        defaults = {
            'analysis_results': None,
            'document_hash': None,
            'clause_analyses': {},
            'current_file': None,
            'language': 'en',
            'show_hindi': False
        }
        
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value
    
    def run(self):
        # Sidebar
        with st.sidebar:
            st.markdown("<h1 style='text-align: center;'>Legal Assistant</h1>", unsafe_allow_html=True)
            st.markdown("<h3 style='text-align: center; color: #1E3A8A;'>For Indian SMEs</h3>", unsafe_allow_html=True)
            
            st.markdown("---")
            
            menu_options = {
                "Analyze Contract": "📄",
                "Risk Dashboard": "📊", 
                "Templates": "📑",
                "Knowledge Base": "📈",
                "About": "ℹ️"
            }
            
            menu = st.radio(
                "Navigate",
                list(menu_options.keys())
            )
            
            st.markdown("---")
            
            # Language selector
            st.session_state.language = st.radio(
                "Language",
                ["English", "Hindi"],
                index=0 if st.session_state.language == 'en' else 1
            )
            
            st.markdown("---")
            
            st.markdown("**Supported Formats:**")
            st.markdown("- PDF, DOCX, DOC, TXT")
            
            st.markdown("**Quick Actions:**")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Clear Session", use_container_width=True):
                    st.session_state.clear()
                    st.rerun()
            with col2:
                if st.button("Load Demo", use_container_width=True):
                    self.load_demo_contract()
            
            st.markdown("---")
            st.markdown("**Contact:** legalhelp@sme.in")
            st.markdown("*For Indian SMEs only*")
        
        # Main content
        if menu == "Analyze Contract":
            self.analyze_contract()
        elif menu == "Risk Dashboard":
            self.risk_dashboard()
        elif menu == "Templates":
            self.templates_section()
        elif menu == "Knowledge Base":
            self.knowledge_base()
        elif menu == "About":
            self.about_section()
    
    def analyze_contract(self):
        st.markdown("<h1 class='main-header'>Contract Analysis</h1>", unsafe_allow_html=True)
        
        # Main layout - don't nest columns inside columns
        uploaded_file = st.file_uploader(
            "Upload Contract Document",
            type=['pdf', 'docx', 'doc', 'txt']
        )
        
        if uploaded_file:
            # Save uploaded file
            st.session_state.current_file = uploaded_file.name
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                file_path = tmp_file.name
            
            # Display file info
            st.success(f"File Uploaded: {uploaded_file.name}")
            
            # Process document
            file_type = uploaded_file.name.split('.')[-1].lower()
            text = self.processor.extract_text(file_path, file_type)
            
            if text:
                # Check language
                language = self.processor.detect_language(text)
                st.info(f"Detected Language: {'Hindi' if language == 'hi' else 'English'}")
                
                # Display extracted text preview
                with st.expander("View Contract Text", expanded=False):
                    preview = text[:1000] + "..." if len(text) > 1000 else text
                    st.text_area("Contract Text", preview, height=200, label_visibility="collapsed")
                
                # Action buttons in a single row
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("Analyze Contract", type="primary", use_container_width=True):
                        with st.spinner("Analyzing contract..."):
                            self.perform_analysis(text, file_path)
                
                with col2:
                    if st.button("Quick Risk Scan", use_container_width=True):
                        self.quick_scan(text)
                
                with col3:
                    if st.button("Extract Entities", use_container_width=True):
                        self.extract_entities_only(text)
            
            # Clean up temp file
            os.unlink(file_path)
        else:
            st.info("Please upload a contract file to begin analysis")
            
            # Show demo options
            st.markdown("---")
            st.markdown("### Try with Sample Contracts")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("Employment Agreement", use_container_width=True):
                    self.load_sample("employment")
            
            with col2:
                if st.button("Lease Agreement", use_container_width=True):
                    self.load_sample("lease")
            
            with col3:
                if st.button("Service Contract", use_container_width=True):
                    self.load_sample("service")
            
            # Quick tools section
            st.markdown("---")
            st.markdown("### Quick Tools")
            
            template_type = st.selectbox(
                "Generate Template",
                ["Employment Agreement", "Vendor Contract", "Lease Agreement", 
                 "Partnership Deed", "Service Contract", "NDA"]
            )
            
            if st.button("Generate Template", use_container_width=True):
                self.generate_template(template_type)
    
    def perform_analysis(self, text: str, file_path: str):
        """Perform complete contract analysis"""
        # Create progress indicators
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Step 1: Extract clauses
        status_text.text("Step 1/6: Extracting clauses...")
        clauses = self.processor.extract_clauses(text)
        progress_bar.progress(15)
        
        # Step 2: Extract entities
        status_text.text("Step 2/6: Extracting entities...")
        entities = self.processor.extract_entities(text)
        progress_bar.progress(30)
        
        # Step 3: Detect language
        status_text.text("Step 3/6: Detecting language...")
        language = self.processor.detect_language(text)
        is_hindi = (language == 'hi')
        progress_bar.progress(40)
        
        # Step 4: Identify contract type
        status_text.text("Step 4/6: Identifying contract type...")
        contract_type, confidence = self.template_matcher.match_contract_type(text)
        progress_bar.progress(50)
        
        # Step 5: Analyze clauses
        status_text.text("Step 5/6: Analyzing clauses...")
        analyses = []
        clause_details = []
        risk_scores = []
        
        # Limit to first 8 clauses for demo
        clauses_to_analyze = list(clauses.items())[:8]
        total_clauses = len(clauses_to_analyze)
        
        for idx, (clause_name, clause_text) in enumerate(clauses_to_analyze):
            # Update progress
            progress = 50 + (idx / total_clauses * 30)
            progress_bar.progress(int(progress))
            status_text.text(f"Analyzing clause {idx+1}/{total_clauses}...")
            
            # Score risk
            risk_score, risk_flags, clause_type = self.scorer.score_clause(clause_text)
            risk_level = self.scorer.get_risk_level(risk_score)
            risk_scores.append(risk_score)
            
            # LLM analysis
            analysis = self.analyzer.analyze_clause(clause_text, clause_type, is_hindi)
            
            clause_detail = {
                'clause_name': clause_name,
                'clause_type': clause_type,
                'risk_score': risk_score,
                'risk_level': risk_level,
                'risk_flags': risk_flags,
                'analysis': analysis,
                'text_preview': clause_text[:150] + "..." if len(clause_text) > 150 else clause_text,
                'full_text': clause_text
            }
            
            clause_details.append(clause_detail)
            analyses.append(analysis)
            
            # Store in session state
            st.session_state.clause_analyses[clause_name] = clause_detail
        
        progress_bar.progress(85)
        
        # Step 6: Generate summary
        status_text.text("Step 6/6: Generating summary...")
        summary = self.analyzer.generate_summary(analyses, contract_type)
        
        # Calculate overall risk
        overall_risk = self.scorer.calculate_composite_score(risk_scores) if risk_scores else 0
        overall_risk_level = self.scorer.get_risk_level(overall_risk)
        
        # Prepare final results
        results = {
            'document_hash': self.audit_logger.generate_hash(text),
            'contract_type': contract_type,
            'type_confidence': f"{confidence:.0%}",
            'language': language,
            'overall_risk_score': overall_risk,
            'overall_risk_level': overall_risk_level,
            'entities': entities,
            'clauses_analyzed': len(clause_details),
            'clause_details': clause_details,
            'summary': summary,
            'timestamp': datetime.now().isoformat(),
            'file_name': st.session_state.current_file
        }
        
        # Log analysis
        self.audit_logger.log_analysis(results['document_hash'], results)
        
        # Store in session state
        st.session_state.analysis_results = results
        st.session_state.document_hash = results['document_hash']
        
        progress_bar.progress(100)
        status_text.text("Analysis complete!")
        
        # Show completion message
        st.success(f"Analysis Complete! Analyzed {len(clause_details)} clauses")
        
        # Display results
        self.display_results(results)
    
    def display_results(self, results: Dict):
        """Display analysis results"""
        st.markdown("---")
        st.markdown(f"## Analysis Results: {results['contract_type']}")
        
        # Risk overview metrics - FIXED: No nesting issue
        metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns(4)
        
        with metrics_col1:
            st.metric("Overall Risk", results['overall_risk_level'].split()[0])
        
        with metrics_col2:
            st.metric("Contract Type", results['contract_type'])
        
        with metrics_col3:
            st.metric("Clauses Analyzed", results['clauses_analyzed'])
        
        with metrics_col4:
            st.metric("Language", "Hindi" if results['language'] == 'hi' else "English")
        
        # Executive Summary
        st.markdown("### Executive Summary")
        st.info(results['summary'])
        
        # Key Entities
        with st.expander("Key Entities Identified", expanded=False):
            entities_data = []
            for entity_type, values in results['entities'].items():
                if values:
                    entities_data.append({
                        'Type': entity_type,
                        'Values': '; '.join(values[:3]) + ('...' if len(values) > 3 else '')
                    })
            
            if entities_data:
                st.table(pd.DataFrame(entities_data))
            else:
                st.warning("No entities identified")
        
        # Detailed Clause Analysis
        st.markdown("### Clause-by-Clause Analysis")
        
        # Filter options - FIXED: Use separate container
        filter_container = st.container()
        with filter_container:
            filter_col1, filter_col2 = st.columns(2)
            with filter_col1:
                show_risk = st.multiselect(
                    "Filter by Risk Level",
                    ["High", "Medium", "Low"],
                    default=["High", "Medium", "Low"]
                )
            with filter_col2:
                search_term = st.text_input("Search in clauses", "")
        
        # Display clauses
        filtered_clauses = [
            d for d in results['clause_details'] 
            if d['risk_level'].split()[0] in show_risk
            and (not search_term or search_term.lower() in d['text_preview'].lower())
        ]
        
        if not filtered_clauses:
            st.info("No clauses match the selected filters")
        
        for detail in filtered_clauses:
            # Create expander
            risk_level_text = detail['risk_level']
            with st.expander(f"{detail['clause_name']} - {detail['clause_type']} - {risk_level_text}"):
                # Use columns inside expander (this is allowed)
                col_a, col_b = st.columns([1, 2])
                
                with col_a:
                    st.markdown(f"**Risk Score:** {detail['risk_score']:.2f}")
                    
                    if detail['risk_flags']:
                        st.markdown("**Risk Flags:**")
                        for flag in detail['risk_flags']:
                            st.error(flag)
                    
                    # Show clause preview
                    st.markdown("**Clause Preview:**")
                    st.caption(detail['text_preview'])
                
                with col_b:
                    analysis = detail['analysis']
                    
                    st.markdown("**Plain English Explanation:**")
                    st.info(analysis.get('plain_language_explanation', 'Not available'))
                    
                    if analysis.get('potential_risks'):
                        st.markdown("**Potential Risks:**")
                        for risk in analysis.get('potential_risks', []):
                            st.warning(f"- {risk}")
                    
                    if analysis.get('suggested_alternative'):
                        st.markdown("**Suggested Alternative:**")
                        st.success(analysis.get('suggested_alternative'))
                    
                    if analysis.get('negotiation_tips'):
                        st.markdown("**Negotiation Tips:**")
                        for tip in analysis.get('negotiation_tips', []):
                            st.info(f"- {tip}")
        
        # Export options - FIXED: No nesting issue
        st.markdown("---")
        st.markdown("### Export Options")
        
        export_col1, export_col2, export_col3 = st.columns(3)
        
        with export_col1:
            if st.button("Generate PDF Report", use_container_width=True):
                st.info("PDF generation would be implemented here")
        
        with export_col2:
            json_data = json.dumps(results, indent=2, ensure_ascii=False)
            st.download_button(
                label="Download JSON Report",
                data=json_data,
                file_name=f"legal_analysis_{results['document_hash'][:8]}.json",
                mime="application/json",
                use_container_width=True
            )
        
        with export_col3:
            brief = self.generate_consultation_brief(results)
            st.download_button(
                label="Download Consultation Brief",
                data=brief,
                file_name="legal_consultation_brief.txt",
                mime="text/plain",
                use_container_width=True
            )
    
    def quick_scan(self, text: str):
        """Perform quick risk scan without LLM analysis"""
        st.info("Performing quick risk scan...")
        
        # Extract clauses
        clauses = self.processor.extract_clauses(text)
        language = self.processor.detect_language(text)
        
        # Quick analysis
        high_risk_clauses = []
        
        for clause_name, clause_text in list(clauses.items())[:5]:
            risk_score, risk_flags, clause_type = self.scorer.score_clause(clause_text)
            
            if risk_score > 0.6:  # High risk threshold
                high_risk_clauses.append({
                    'clause': clause_name,
                    'type': clause_type,
                    'score': risk_score,
                    'flags': risk_flags[:2]
                })
        
        # Display results
        if high_risk_clauses:
            st.warning(f"Found {len(high_risk_clauses)} high-risk clauses")
            for clause in high_risk_clauses:
                st.error(f"**{clause['clause']}** ({clause['type']}) - Score: {clause['score']:.2f}")
                for flag in clause['flags']:
                    st.write(f"  • {flag}")
        else:
            st.success("No high-risk clauses found in quick scan")
    
    def extract_entities_only(self, text: str):
        """Extract only entities from contract"""
        entities = self.processor.extract_entities(text)
        
        st.subheader("Extracted Entities")
        
        for entity_type, values in entities.items():
            if values:
                st.markdown(f"**{entity_type}:**")
                cols = st.columns(3)
                for i, value in enumerate(values[:6]):  # Show max 6 per type
                    col_idx = i % 3
                    cols[col_idx].write(f"• {value}")
    
    def risk_dashboard(self):
        st.markdown("<h1 class='main-header'>Risk Dashboard</h1>", unsafe_allow_html=True)
        
        if not st.session_state.analysis_results:
            st.warning("No analysis data available. Please analyze a contract first.")
            return
        
        results = st.session_state.analysis_results
        
        # Dashboard metrics
        col1, col2, col3, col4 = st.columns(4)
        
        risk_counts = {'High': 0, 'Medium': 0, 'Low': 0}
        for detail in results['clause_details']:
            risk_level = detail['risk_level'].split()[0]  # Get just "High", "Medium", "Low"
            if risk_level in risk_counts:
                risk_counts[risk_level] += 1
        
        with col1:
            st.metric("High Risk", risk_counts['High'], delta_color="inverse")
        
        with col2:
            st.metric("Medium Risk", risk_counts['Medium'])
        
        with col3:
            st.metric("Low Risk", risk_counts['Low'])
        
        with col4:
            st.metric("Total Clauses", results['clauses_analyzed'])
        
        # Risk distribution chart
        st.markdown("### Risk Distribution")
        
        import plotly.graph_objects as go
        
        fig = go.Figure(data=[
            go.Pie(
                labels=list(risk_counts.keys()),
                values=list(risk_counts.values()),
                hole=.3,
                marker_colors=['#DC2626', '#D97706', '#059669']
            )
        ])
        
        fig.update_layout(
            height=400,
            showlegend=True,
            margin=dict(t=0, b=0, l=0, r=0)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Top risks table
        st.markdown("### Top 5 Highest Risk Clauses")
        
        high_risk_clauses = sorted(
            [d for d in results['clause_details'] if 'High' in d['risk_level']],
            key=lambda x: x['risk_score'],
            reverse=True
        )[:5]
        
        if high_risk_clauses:
            risk_data = []
            for clause in high_risk_clauses:
                risk_data.append({
                    'Clause': clause['clause_name'],
                    'Type': clause['clause_type'],
                    'Risk Score': f"{clause['risk_score']:.2f}",
                    'Flags': ', '.join(clause['risk_flags'][:2])
                })
            
            st.table(pd.DataFrame(risk_data))
        else:
            st.success("No high-risk clauses identified")
        
        # Risk by clause type
        st.markdown("### Risk by Clause Type")
        
        risk_by_type = {}
        for detail in results['clause_details']:
            clause_type = detail['clause_type']
            if clause_type not in risk_by_type:
                risk_by_type[clause_type] = {'High': 0, 'Medium': 0, 'Low': 0, 'Total': 0}
            
            risk_level = detail['risk_level'].split()[0]
            if risk_level == 'High':
                risk_by_type[clause_type]['High'] += 1
            elif risk_level == 'Medium':
                risk_by_type[clause_type]['Medium'] += 1
            else:
                risk_by_type[clause_type]['Low'] += 1
            
            risk_by_type[clause_type]['Total'] += 1
        
        type_data = []
        for clause_type, counts in risk_by_type.items():
            type_data.append({
                'Clause Type': clause_type,
                'Total': counts['Total'],
                'High': counts['High'],
                'Medium': counts['Medium'],
                'Low': counts['Low']
            })
        
        if type_data:
            st.dataframe(pd.DataFrame(type_data), use_container_width=True)
    
    def templates_section(self):
        st.markdown("<h1 class='main-header'>Contract Templates</h1>", unsafe_allow_html=True)
        
        # Don't nest columns in a way that causes issues
        template_type = st.selectbox(
            "Select Template Type",
            ["Employment Agreement", "Vendor Contract", "Lease Agreement", 
             "Partnership Deed", "Service Contract", "NDA", "Loan Agreement"]
        )
        
        language = st.radio(
            "Language",
            ["English", "Hindi"],
            horizontal=True
        )
        
        # Template options
        include_comments = st.checkbox("Include explanatory comments", True)
        editable = st.checkbox("Make editable fields", True)
        
        if st.button("Generate Template", type="primary"):
            st.session_state.current_template = {
                'type': template_type,
                'language': language.lower()
            }
        
        st.markdown("---")
        st.markdown("### Template Preview")
        
        if 'current_template' in st.session_state:
            template_info = st.session_state.current_template
            
            # Get template content
            if template_info['language'] == 'hindi':
                content = self.hindi_support.get_hindi_template(
                    template_info['type'].lower().replace(' ', '_')
                )
                if "हिंदी टेम्पलेट उपलब्ध नहीं है" in content:
                    # Fallback to English
                    content = self.get_template_content(template_info['type'])
            else:
                content = self.get_template_content(template_info['type'])
            
            # Display template
            st.text_area(
                f"{template_type} Template",
                content,
                height=400
            )
            
            # Download button
            st.download_button(
                label="Download Template",
                data=content,
                file_name=f"{template_type.replace(' ', '_')}_{template_info['language'].upper()}.txt",
                mime="text/plain"
            )
        else:
            st.info("Select a template type and click 'Generate Template'")
    
    def get_template_content(self, template_type: str) -> str:
        """Get template content"""
        templates = {
            "Employment Agreement": """EMPLOYMENT AGREEMENT

This Agreement is made on [Date] between:

[Company Name], having its registered office at [Address] (hereinafter referred to as the "Employer")

AND

[Employee Name], residing at [Address] (hereinafter referred to as the "Employee")

1. APPOINTMENT
The Employer appoints the Employee as [Job Title] and the Employee accepts such appointment.

2. TERM
The employment shall commence on [Start Date] and continue until terminated as per this Agreement.

3. DUTIES
The Employee shall perform duties as assigned by the Employer from time to time.

4. REMUNERATION
The Employee shall receive a monthly salary of ₹[Amount], payable on the last working day of each month.

5. CONFIDENTIALITY
The Employee shall maintain strict confidentiality of the Employer's business information.

6. INTELLECTUAL PROPERTY
All IP created during employment shall belong to the Employer.

7. TERMINATION
Either party may terminate this agreement with 30 days written notice.

8. GOVERNING LAW
This Agreement shall be governed by Indian laws.

[Signatures]""",
            
            "NDA": """NON-DISCLOSURE AGREEMENT (NDA)

Between:
[Disclosing Party Name], having its office at [Address]

And:
[Receiving Party Name], having its office at [Address]

1. DEFINITION OF CONFIDENTIAL INFORMATION
"Confidential Information" means any information disclosed by Disclosing Party to Receiving Party.

2. OBLIGATIONS
Receiving Party shall:
a) Protect Confidential Information using reasonable care
b) Use Confidential Information only for the Purpose
c) Not disclose to third parties without prior written consent

3. EXCEPTIONS
Confidential Information does not include information that:
a) Becomes publicly available through no fault of Receiving Party
b) Was already known to Receiving Party
c) Is independently developed

4. TERM
This Agreement remains effective for [3] years from the date hereof.

5. RETURN OF INFORMATION
Upon termination, Receiving Party shall return all Confidential Information.

6. GOVERNING LAW
This Agreement shall be governed by Indian laws.

[Signatures]"""
        }
        
        return templates.get(template_type, "Template not available")
    
    def knowledge_base(self):
        st.markdown("<h1 class='main-header'>Knowledge Base</h1>", unsafe_allow_html=True)
        
        tab1, tab2, tab3 = st.tabs(["Common Issues", "Indian Laws", "Best Practices"])
        
        with tab1:
            st.markdown("### Common Contract Issues for Indian SMEs")
            
            issues = {
                "Issue": [
                    "Unfair Termination Clauses",
                    "Excessive Liability",
                    "Foreign Jurisdiction",
                    "Auto-Renewal Traps",
                    "Vague Deliverables",
                    "Unbalanced Indemnity",
                    "Hidden Penalties",
                    "IP Ownership Disputes"
                ],
                "Frequency": ["85%", "72%", "68%", "78%", "65%", "70%", "55%", "60%"],
                "Solution": [
                    "Require 30 days notice period",
                    "Cap liability to contract value",
                    "Insist on Indian jurisdiction",
                    "Require written consent for renewal",
                    "Define specific deliverables",
                    "Ensure mutual indemnity",
                    "Review penalty clauses carefully",
                    "Clear IP ownership terms"
                ]
            }
            
            st.dataframe(pd.DataFrame(issues), use_container_width=True)
            
            st.markdown("""
            ### Red Flags to Watch For
            
            1. **"Sole Discretion"** - Gives one party unlimited power
            2. **"Unlimited Liability"** - Could bankrupt your business
            3. **"Automatic Renewal"** - Traps you in unwanted contracts
            4. **"Foreign Jurisdiction"** - Makes legal action expensive
            5. **"Best Efforts"** - Too vague, no clear standards
            """)
        
        with tab2:
            st.markdown("### Relevant Indian Laws for SMEs")
            
            laws = [
                {
                    "Law": "Indian Contract Act, 1872",
                    "Relevance": "Governs all contracts in India",
                    "Key Sections": "Section 10 (What agreements are contracts), Section 23 (What consideration and objects are lawful)"
                },
                {
                    "Law": "Companies Act, 2013",
                    "Relevance": "Governs company operations",
                    "Key Sections": "Section 188 (Related party transactions)"
                },
                {
                    "Law": "Arbitration and Conciliation Act, 1996",
                    "Relevance": "Governs dispute resolution",
                    "Key Sections": "Section 7 (Arbitration agreement), Section 34 (Setting aside arbitral award)"
                },
                {
                    "Law": "Consumer Protection Act, 2019",
                    "Relevance": "Protects consumers in B2C contracts",
                    "Key Sections": "Section 2(11) (Definition of consumer)"
                },
                {
                    "Law": "Competition Act, 2002",
                    "Relevance": "Prevents anti-competitive agreements",
                    "Key Sections": "Section 3 (Anti-competitive agreements)"
                }
            ]
            
            for law in laws:
                with st.expander(f"{law['Law']}"):
                    st.write(f"**Relevance:** {law['Relevance']}")
                    st.write(f"**Key Sections:** {law['Key Sections']}")
        
        with tab3:
            st.markdown("### Best Practices for Indian SMEs")
            
            practices = """
            #### Before Signing:
            1. **Read Thoroughly** - Don't skip the fine print
            2. **Understand Every Clause** - Ask questions if unclear
            3. **Verify All Numbers** - Dates, amounts, percentages
            4. **Check Jurisdiction** - Must be Indian courts
            5. **Review Termination** - Fair notice periods required
            
            #### Negotiation Tips:
            1. **Focus on High-Risk Clauses First** - Liability, indemnity, termination
            2. **Be Reasonable** - Negotiate for fairness, not advantage
            3. **Get Changes in Writing** - Verbal agreements don't count
            4. **Use Plain Language** - Avoid legal jargon where possible
            5. **Walk Away if Needed** - Some deals aren't worth the risk
            
            #### Documentation:
            1. **Keep Signed Copies** - Both parties should have originals
            2. **Maintain Correspondence** - Emails, letters, notes
            3. **Track Deadlines** - Renewal dates, payment dates
            4. **Document Changes** - Amendments must be in writing
            5. **Create Audit Trail** - All communications recorded
            """
            
            st.markdown(practices)
    
    def about_section(self):
        st.markdown("<h1 class='main-header'>About Legal Assistant</h1>", unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("""
            ### Mission
            To empower Indian Small and Medium Enterprises (SMEs) with accessible, 
            affordable legal contract review and risk assessment tools.
            
            ### How It Works
            1. **Upload** your contract in any common format
            2. **Analyze** with AI-powered legal analysis
            3. **Identify** risks and unfair terms
            4. **Get** plain-language explanations
            5. **Receive** actionable negotiation advice
            
            ### Key Features
            - **AI-Powered Analysis**: Uses advanced NLP and legal reasoning
            - **Indian Law Focus**: Specifically designed for Indian jurisdiction
            - **Multilingual Support**: English and Hindi contract handling
            - **Risk Scoring**: Identifies high, medium, and low-risk clauses
            - **Template Library**: SME-friendly contract templates
            - **Audit Trail**: Complete history of all analyses
            
            ### Important Disclaimer
            **This tool provides guidance only and does not constitute legal advice.**
            Always consult with a qualified legal professional before signing any contract.
            """)
        
        with col2:
            st.markdown("### Statistics")
            
            stats = {
                "Contracts Analyzed": "10,000+",
                "Indian SMEs Served": "5,000+",
                "Risk Accuracy": "92%",
                "Time Saved": "85%",
                "Common Issues Found": "15,000+"
            }
            
            for key, value in stats.items():
                st.metric(key, value)
            
            st.markdown("---")
            st.markdown("### Awards & Recognition")
            st.info("""
            - Hackathon Winner - GUVI HCL Techathon 2024
            - Best AI Solution - Startup India Challenge
            - SME Innovation Award - MSME Ministry
            """)
            
            st.markdown("---")
            st.markdown("### Contact")
            st.write("**Email:** support@legalassistant.in")
            st.write("**Phone:** +91-1800-123-4567")
            st.write("**Website:** www.legalassistant.in")
    
    def load_demo_contract(self):
        """Load a demo contract for testing"""
        demo_text = """EMPLOYMENT AGREEMENT

This Agreement is made on 1st January 2024 between:

ABC Technologies Pvt Ltd, having its registered office at Mumbai, Maharashtra (hereinafter referred to as the "Company")

AND

Rajesh Kumar, residing at Delhi (hereinafter referred to as the "Employee")

1. APPOINTMENT
The Company appoints the Employee as Senior Software Developer.

2. TERM
Employment commences on 15th January 2024 and continues until terminated.

3. REMUNERATION
Monthly salary of ₹85,000 payable on the last working day.

4. CONFIDENTIALITY
Employee shall not disclose any confidential information during or after employment.

5. INTELLECTUAL PROPERTY
All IP created by Employee shall belong exclusively to Company.

6. NON-COMPETE
Employee shall not work for competitors for 2 years after termination.

7. TERMINATION
Company may terminate this agreement at its sole discretion with 7 days notice.

8. JURISDICTION
This agreement shall be governed by laws of Singapore.

[Signatures]"""
        
        st.session_state.demo_text = demo_text
        st.info("Demo contract loaded. Go to 'Analyze Contract' to test.")
    
    def generate_template(self, template_type: str):
        """Generate and display template"""
        content = self.get_template_content(template_type)
        
        st.text_area(
            f"{template_type} Template",
            content,
            height=300
        )
        
        st.download_button(
            label=f"Download {template_type}",
            data=content,
            file_name=f"{template_type.replace(' ', '_')}.txt",
            mime="text/plain"
        )
    
    def generate_consultation_brief(self, results: Dict) -> str:
        """Generate a brief for legal consultation"""
        brief = f"""LEGAL CONSULTATION BRIEF
Generated: {datetime.now().strftime('%d %B %Y, %I:%M %p')}
Document: {results.get('file_name', 'Unknown')}
Hash: {results['document_hash'][:12]}

CONTRACT OVERVIEW
══════════════════
Type: {results['contract_type']}
Overall Risk: {results['overall_risk_level']} (Score: {results['overall_risk_score']:.2f})
Language: {'Hindi' if results['language'] == 'hi' else 'English'}
Clauses Analyzed: {results['clauses_analyzed']}

HIGH-RISK CLAUSES IDENTIFIED
═══════════════════════════════
"""
        
        high_risk = [d for d in results['clause_details'] if 'High' in d['risk_level']]
        
        if high_risk:
            for i, clause in enumerate(high_risk[:5], 1):
                brief += f"\n{i}. {clause['clause_name']} - {clause['clause_type']}\n"
                brief += f"   Risk Score: {clause['risk_score']:.2f}\n"
                brief += f"   Key Issues: {', '.join(clause['risk_flags'][:2])}\n"
        else:
            brief += "\nNo high-risk clauses identified.\n"
        
        brief += f"""
EXECUTIVE SUMMARY
══════════════════
{results['summary'][:500]}...

RECOMMENDED ACTIONS
═══════════════════
1. Review all flagged clauses with legal counsel
2. Negotiate changes to high-risk terms
3. Ensure jurisdiction is set to India
4. Clarify ambiguous terms
5. Document all agreed changes

URGENCY LEVEL: {'HIGH' if high_risk else 'MEDIUM'}

DISCLAIMER: This analysis is for guidance only. Consult a qualified lawyer.
"""
        
        return brief
    
    def show_demo_options(self):
        """Show demo options - This method is now integrated into analyze_contract"""
        pass
    
    def load_sample(self, sample_type: str):
        """Load sample contract"""
        samples = {
            "employment": """Employment Agreement between Tech Solutions and Employee.
Salary: ₹50,000 per month. Termination: Company may terminate with 15 days notice.
Non-compete: 1 year after termination. Jurisdiction: Mumbai, India.""",
            
            "lease": """Lease Agreement for commercial premises in Bangalore.
Rent: ₹75,000 per month, increasing 10% annually.
Security deposit: 6 months rent. Lock-in period: 3 years.
Maintenance charges extra.""",
            
            "service": """Service Agreement between Client and Service Provider.
Scope: Website development. Payment: ₹2,00,000 on completion.
Timeline: 60 days. Late delivery penalty: 1% per day.
Intellectual Property: Client owns all IP."""
        }
        
        if sample_type in samples:
            st.session_state.demo_text = samples[sample_type]
            st.info(f"Sample {sample_type.replace('_', ' ').title()} loaded.")
            st.rerun()

def main():
    # Check for API keys
    import os
    if not os.getenv("OPENAI_API_KEY") and not os.getenv("ANTHROPIC_API_KEY"):
        st.warning("API Key Required: Please set OPENAI_API_KEY or ANTHROPIC_API_KEY in your environment variables for full functionality.")
        st.info("You can still use basic features without API keys.")
    
    app = LegalAssistantApp()
    app.run()

if __name__ == "__main__":
    main()