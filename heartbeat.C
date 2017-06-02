void heartbeat(){

  gErrorIgnoreLevel = kWarning;
  gStyle->SetPadTickX(1);
  gStyle->SetPadTickY(1);
  gStyle->SetPadTopMargin(0.05);
  gStyle->SetPadRightMargin(0.07);
  gStyle->SetPadBottomMargin(0.16);
  gStyle->SetPadLeftMargin(0.19);

  double xlo, xhi, xav, yin;
  std::vector<double> xlos, xhis, xavs, yins;
  std::string line;
  std::ifstream ifile("heartbeat.dat");
  while(std::getline(ifile, line)){
    std::stringstream ss;
    ss << line;
    ss >> xlo; ss >> xhi; ss >> yin;
    xav = (xhi+xlo)/2.0;
    xavs.push_back(xav);
    xlos.push_back(std::fabs(xav-xlo));
    xhis.push_back(std::fabs(xav-xhi));
    yins.push_back(yin);
  }

  int n = xavs.size();
  Double_t xl[n], xh[n], x[n];
  Double_t yl[n], yh[n], y[n];
  for (int i=0; i < n; i++){
    xl[i] = xlos[i];
    xh[i] = xhis[i];
    x[i]  = xavs[i];
    yl[i] = 0;
    yh[i] = 0;
    y[i]  = yins[i];
  }

  TCanvas *canv = new TCanvas("canv", "canv", 800, 800);
  canv->SetFillColor(0);
  canv->SetGrid();

  TGraphAsymmErrors* gr = new TGraphAsymmErrors(n, x, y, xl, xh, yl, yh);
  gr->SetLineColor(kRed);
  gr->SetMarkerColor(kRed);
  gr->SetMarkerStyle(kCircle);
  gr->GetXaxis()->SetTitleSize(0.05);
  gr->GetYaxis()->SetTitleSize(0.05);
  gr->GetXaxis()->SetLabelSize(0.05);
  gr->GetYaxis()->SetLabelSize(0.05);
  gr->GetXaxis()->SetTitleOffset(1.5);
  gr->GetYaxis()->SetTitleOffset(1.8);
  gr->GetXaxis()->SetNdivisions(505);
  gr->GetYaxis()->SetNdivisions(505);
  gr->SetTitle("");
  gr->GetXaxis()->SetTitle("Days since start of script");
  gr->GetYaxis()->SetTitle("Trigger rate [Hz]");
  gr->Draw("AP");

  canv->Update();
  canv->SaveAs("heartbeat.pdf");
}
