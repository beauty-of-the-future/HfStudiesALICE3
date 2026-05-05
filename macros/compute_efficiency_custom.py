#!/usr/bin/env python3

import argparse
import uproot
import numpy as np
from alive_progress import alive_bar

import ROOT

def set_obj_style(obj, color, marker=ROOT.kFullCircle, fillstyle=-1, alpha=1.1):
    """
    Set style
    """
    if isinstance(obj, ROOT.TH1):
        obj.SetDirectory(0)
    obj.SetLineWidth(2)
    obj.SetLineColor(color)
    obj.SetMarkerColor(color)
    obj.SetMarkerStyle(marker)
    if fillstyle > -1:
        obj.SetFillStyle(fillstyle)
        obj.SetFillColorAlpha(color, alpha)

def compare(input_file_rec, input_file_gen, output_file):
    """
    Main function for efficiency comparison

    --------------------------------
    PARAMETERS
    input_files: list of input file names
    """

    ROOT.gStyle.SetPadTickX(1)
    ROOT.gStyle.SetPadTickY(1)
    ROOT.gStyle.SetPadLeftMargin(0.15)
    ROOT.gStyle.SetPadBottomMargin(0.14)
    ROOT.gStyle.SetPadTopMargin(0.035)
    ROOT.gStyle.SetPadRightMargin(0.035)
    ROOT.gStyle.SetTitleSize(0.045, "xy")
    ROOT.gStyle.SetLabelSize(0.045, "xy")
    ROOT.gStyle.SetTitleOffset(1.3, "x")
    ROOT.gStyle.SetOptStat(0)
    ROOT.gStyle.SetOptTitle(0)

    pt_bins = [0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.8, 1.0, 1.5, 2.0, 3.0, 5.0, 10.]
    labels = ["light", "beauty"]
    hist_rec = {
        0: ROOT.TH1D("hist_rec_light", ";#it{p}_{T} (Gev/#it{c});#it{N}_{rec}", len(pt_bins)-1, np.array(pt_bins, np.float64)),
        5: ROOT.TH1D("hist_rec_beauty", ";#it{p}_{T} (Gev/#it{c});#it{N}_{rec}", len(pt_bins)-1, np.array(pt_bins, np.float64)),
    }
    hist_gen = {
        0: ROOT.TH1D("hist_gen_light", ";#it{p}_{T} (Gev/#it{c});#it{N}_{gen}", len(pt_bins)-1, np.array(pt_bins, np.float64)),
        5: ROOT.TH1D("hist_gen_beauty", ";#it{p}_{T} (Gev/#it{c});#it{N}_{gen}", len(pt_bins)-1, np.array(pt_bins, np.float64)),
    }

    df_gen = uproot.open(input_file_gen)["particles"].arrays(library="pd")
    df_gen.query("abs(eta) < 1.44", inplace=True)
    df_gen["radius"] = np.sqrt(df_gen["vx"]**2 + df_gen["vy"]**2)
    for ipt, (pt_min, pt_max) in enumerate(zip(pt_bins[:-1], pt_bins[1:])):
        df_gen_pt = df_gen.query(f"{pt_min} < pt < {pt_max} and abs(particle_type) == 211")
        df_gen_pt_light = df_gen_pt.query("hf_origin == 0 and radius < 0.1") # only primary pions
        df_gen_pt_beauty = df_gen_pt.query("hf_origin == 5")
        hist_gen[0].SetBinContent(ipt+1, len(df_gen_pt_light))
        hist_gen[5].SetBinContent(ipt+1, len(df_gen_pt_beauty))
        hist_gen[0].SetBinError(ipt+1, np.sqrt(len(df_gen_pt_light)))
        hist_gen[5].SetBinError(ipt+1, np.sqrt(len(df_gen_pt_beauty)))

    df_rec = uproot.open(input_file_rec)["tracksummary"].arrays(library="pd")
    df_rec.query("abs(t_eta) < 1.44", inplace=True)
    n_events = len(np.unique(df_rec["event_nr"]))
    with alive_bar(n_events) as bar:
        for event_nr in np.unique(df_rec["event_nr"]):
            df_rec_ev = df_rec.query(f"event_nr == {event_nr}")
            df_gen_ev = df_gen.query(f"event_id == {event_nr}")
            for pt, part_id, vtx_id in zip(df_rec_ev["t_pT"].to_numpy(),
                                           df_rec_ev["majorityParticleId_particle"].to_numpy(),
                                           df_rec_ev["majorityParticleId_vertex_primary"].to_numpy()):
                part = df_gen_ev[(df_gen_ev["particle"] == part_id) & (df_gen_ev["vertex_primary"] == vtx_id)]
                orig = part["hf_origin"].values[0] # we check the origin
                pdg = part["particle_type"].values[0] # we check the pdg
                radius = part["radius"].values[0] # we check the production radius
                if (orig == 5 or (orig == 0 and radius < 0.1)) and abs(pdg) == 211:
                    hist_rec[orig].Fill(pt)
            bar()


    leg = ROOT.TLegend(0.4, 0.2, 0.9, 0.4)
    leg.SetTextSize(0.04)
    leg.SetFillStyle(0)
    leg.SetBorderSize(0)
    leg.SetHeader("#splitline{HardQCD:bbbar pp, no pileup}{#pi^{#pm} |#it{#eta}| < 1.44}")
    hist_eff = {}
    orig_labels = {0: "light", 5: "beauty"}
    leg_labels = {0: "light primary", 5: "beauty"}
    orig_colors = {0: ROOT.kGreen+2, 5: ROOT.kAzure+4}
    for orig in hist_rec.keys():
        hist_rec[orig].Sumw2()
        hist_eff[orig] = hist_rec[orig].Clone(f"hist_eff_{orig_labels[orig]}")
        hist_eff[orig].Divide(hist_rec[orig], hist_gen[orig], 1., 1., "B")
        set_obj_style(hist_rec[orig], orig_colors[orig])
        set_obj_style(hist_gen[orig], orig_colors[orig])
        set_obj_style(hist_eff[orig], orig_colors[orig])
        leg.AddEntry(hist_eff[orig], leg_labels[orig], "lp")

    canv = ROOT.TCanvas("canv", "", 500, 500)
    canv.DrawFrame(0.05, 0., 10., 1., ";#it{p}_{T} (GeV/#it{c});tracking efficiency")
    canv.cd().SetLogx()
    for orig in hist_rec.keys():
        hist_eff[orig].Draw("same")
    leg.Draw()
    canv.SaveAs(output_file.replace(".root", ".pdf"))

    outfile = ROOT.TFile(output_file, "recreate")
    for orig in hist_rec.keys():
        hist_gen[orig].Write()
        hist_rec[orig].Write()
        hist_eff[orig].Write()
    outfile.Close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Arguments")
    parser.add_argument("--infile_rec", "-ir", metavar="text",
                        default="tracksummary_ambi.root", help="Input file for reconstructed tracks")
    parser.add_argument("--infile_gen", "-ig", metavar="text",
                        default="particles.root", help="Input file for generated particles")
    parser.add_argument("--outfile", "-o", metavar="text",
                        default="efficiency.root", help="Output file name")
    args = parser.parse_args()

    compare(args.infile_rec, args.infile_gen, args.outfile)
