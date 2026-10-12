"""Standalone mesh-derived CAD code, with embedded vertex and triangle data.

This reconstructs a faceted BREP, not an inferred sketch/extrusion feature tree.
Original numeric coordinates are retained; physical STL units are unknown.
Open meshes remain CAD surfaces. No guessed closures or thickness are added.
Run: python part_XXX_cad.py [--output-directory PATH] [--no-validate]
"""
from pathlib import Path
import argparse,base64,io,json,time,zlib
import numpy as np
import cadquery as cq
from OCP.BRepBuilderAPI import BRepBuilderAPI_Sewing

PART_NAME = 'part_007'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/8512669067e448a9b1d3fb78bf0c61c6/part_007.stl', 'relative_path': '8512669067e448a9b1d3fb78bf0c61c6/part_007.stl', 'source_sha256': '8e60689e60450e7d6bdd0fe74afdc6fa1323609890c331c9ad32419eadc1a9e8', 'input_faces': 144, 'input_vertices': 120, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.027921658009290695, 0.2726280987262726, -0.13230469822883606], [0.06397952139377594, 0.3813461661338806, -0.004131302237510681]]}
GEOMETRY_BASE85 = 'c$}q}3s6+o9mX%>3o#KDQB-u*2pADi5Htq4i6Sah!59_mW08jtP|2bYU(7WY5eT9@)%e&N>nl}bG^ry-u8CulPHLJaHaI%dO&U#W5^dAOhFFu{^ZmayOJ_UNX?Ny7-|v2&`#;Zn&XLp<-;RNr{Dx@f{fc^;{+gzuyB4SwXFFEqWo8#et|(mNqXocMKeyJ+e0oM|x{p?@tqaS_F3NO-J!T7gJZD^3ge@#*rDK&NW5tq{j;w6uPsu1K%C`KX+>F9(>p6V%nCJ*w%!mlv2HXGm>!zAg+O)exY0{1N6IGj@*z=lt)&f7<snnM98hmqW{;Me0>29M^J)+wO%C}ugIF0h_KCFW-_~Ikw>$iTlPdyu%t+h(+C$Ih<<u7KRM4r$q@SX1zqr5gNbuZq3IB6T|?e?+c8R!2Z{Dx~a$dgws<z1`A@46Mf-jIj<dO*k<@H^4JR*UxQ+eV#$e>`g|@`rwh_UkY8c?Ipv?@<L^Il2}8fE(z)@tfdE=--Z`UL!Ag2lAfE-GcTsUHJq2y?MLPuT>M^Ywz5b@rk>C1n(c3yIHBLp{L|22|yn6bk)!B@5d)ef8#nfdHT-S{%DW!MLc|c_2(P$?>{t4f1A%A!~5Yu@NLb_sMl}|ZHE6{WGU)>@h$k;`ui`VeRbELMft<WBu{*C3;g8j0+dhaEA6R`YVh>+Ura%J%wHCZ|J<!yw5M&EjN2z2u|BkSM`a^VOPh>O$f|nyX1))`t=0EK_;>6wU&ht`$Xl=u^JVm2igD9i`_nLvMc0r=YfX@KrU&LFdW@TKb635m|6ttwH^Mh&?_YuUV-L$Z%v_HAX3D{mM34E^{q`fjar-8G`@NCU-@z?XZ_1f9D4%gz#%)Q7i97|{OX0VUL>}|jMbxX;T-k_v-yV+s+OCzK$GqO%^E~{&mPz{~5>VbY<3PE3cJ*!(|L?c4UiIqt;p^dDWjyCqmSG(0hi^eU8)IaA))$sZJJaDi_idGa`KNEkeC%GcMb?LT1?B77Hlh7#ODj<C`FWB*^eon^_R{n4ZB^$a|Lq&q7@t{vEAhNCNcwxzf&9)TE%42=Z%h91_tv5Oh4LyqC)G*6g0G-oX5eA?_I^Q<fAgZX@QVvyK)Vn9TH2GhphCXqP2#8OQhs^GdX(RA5x$u*T=HvI(N6v7scMu9UMA%a_b||}X^U&{eCY$p-)~Wwr|<f#QS$8hGwL<_2W&(6FJol?$xOp{ZjLOjMY&JEl=ZOi4%UMfLI2exnfIun@_j{$Z+pWb`_id%2io~hIVI1c&Igg7zEQSA+OvNy+UcUN4Xl)L{%y!6Pv4c_Ab!a8QcvF&H(kczOsC>@zTaw&&$nwmeSO0p#b5pP#&-3#CdxQeEWkdcMTzfx_dTiipPv_c`bN}X$rByrz<QW;z24h+YTu7<@H+nE6B@kDmtN7U(cAnQf7;yWZ9SNUM;pDapP{E4y{$K+U!Nv#>r>wl-sEjPYef}J-qyd_7Qdt2_Z24JmvLzee7$~-l)rZf^}1?K>}dC$*2{NlKhv_q^Sd_rUEAxf!hf(2Y><7xT&V3te)qmHU-k|2UJ(2T`^?weXNFye@2rTF^4qE~FUFf+!8giJOM6Oc%9U@c3f_f0zDKy9e2?=|TN4W39^@nKiFgiq^zA;o@yz{D=YFVX1?)xnqovZGL0xf<xF(mvckj1$_kKH}ejlFGl4bq8IaSKPHQ0&rixbfvJ?I78GhDOh!*|tI$bR^Gf82ZY{7U%lbHU)bpr7~{zPWXYl%F&a<+WjZelGKyiTp<OWt_9-t>fY!*(vq*T8erN|FQe=d?Q-&<a~pD-hLq$zWcn>0_D8Z%h$qppN}TbN29U^zUwbjWZnzT;=W;=KY0M(FVAtqeU7KhIf%S>rpkCO9f13izWxk++dtx^J+ps>bKHErS$y6fO!xg^`5pM~`-XN-?i<dG35Srk?7rmrDg@)>%1b|tb{>6C{BJ||ApfTo@a^mBWxj4Lg0EkWJA!iEw@bfnl;B?E{A410d&@_X=W3hWivs2!#WU}F2Jd@DPx`#?*|y7l&w0W1GV<{LY4HAO)ZRIU^1R17d5<-Nb5G!X-h1sea_`me+FwEYcu#h!dva>K+yC(&?ti0qv5H#ZXWjmDGCZ#S%2YqMdcXST#r}6!|Jd07_v*jYYD10{3#=GV9mi0-keWkYNY16^lXJ-q>T0rsT*6RXOkG7TCKpi)$VKFAs-3KK0y&%f7(?*@>R__cUgQB}KWay^AK8c6f$T$e{}gwn_9k~F_o4PD_aP6ZK0<zk<EvQx-%Bl>hpkApVzCwTshQ-NR{X?@Neso4tr)A;krhuc6elwjPo*Z3r;?{rCzB^L=X8eRrx=RoP-l|okkc57CsHSoCz2x>ileEM$<gF7)I{<aax7IR>+EwZL-A;a;utHUsPWXX<gpy1c!uI98H$sr$>bT-Y1Cx$G;#`cDmjHbi#nY=o#Qx*p?EHJ4tXv)otj2YC(mOjPM}UCCy*bdMv@;Thf$-+VdQY?7;-pyBsG>C%kdq_P#nQfJc=4a?rBA5P5s$Jv<taAIe^-O96%1D29txxAyy2s!e+&AY6y8ac^EaAJc>Gy8cYsm9RnGPAEI_4KSb`tQ0z<XO!g)FQ+tyA$^EE($^FPfsDsFZ*oPqu#UrT0$nO4(pvI8hYkdSmaVSG^95tS-^ht6Y`EiEgDbysg`x}_TQ2aDQ@oefe@)9e4YDI<>%dJ>p#j^~>h18YgLh>`zJn}Q-Eb20H7I_ghgPfY;(;?9JKmF<L$Dg4#@^*iS`}a57AKRX9esAS^aEPa-bW(F}9RMBBxixCX*Zu`l9Xcl'

def decode_geometry():
    with np.load(io.BytesIO(zlib.decompress(base64.b85decode(GEOMETRY_BASE85)))) as data:
        return data['vertices'],data['faces']

def build():
    vertices,faces=decode_geometry()
    center=(vertices.min(axis=0)+vertices.max(axis=0))/2
    extent=float(np.ptp(vertices,axis=0).max())
    if extent<=0: raise ValueError('Source has zero extent')
    construction_scale=100.0/extent
    v=(vertices-center)*construction_scale
    sewing=BRepBuilderAPI_Sewing(1e-7,True,True,True,False)
    planar_faces=[]
    skipped=[]
    for index,tri in enumerate(faces):
        points=v[tri]
        if np.linalg.norm(np.cross(points[1]-points[0],points[2]-points[0]))<=1e-12:
            skipped.append(index)
            continue
        wire=cq.Wire.makePolygon([cq.Vector(*p) for p in points],close=True)
        face=cq.Face.makeFromWires(wire)
        planar_faces.append(face)
        sewing.Add(face.wrapped)
    if not planar_faces: raise ValueError('No non-degenerate triangles')
    sewing.Perform()
    shape=cq.Shape.cast(sewing.SewedShape())
    representation='faceted_surface'
    if SOURCE_INFO['input_watertight']:
        solids=[]
        for shell in shape.Shells():
            solid=cq.Solid.makeSolid(shell)
            if solid.Volume()<0: solid=cq.Shape.cast(solid.wrapped.Reversed())
            solids.append(solid)
        if solids:
            candidate=solids[0] if len(solids)==1 else cq.Compound.makeCompound(solids)
            if candidate.isValid() and len(candidate.Faces())==len(planar_faces):
                shape=candidate
                representation='faceted_solid'
    if not shape.isValid():
        # Explicitly represent troublesome nonmanifold edges as separate faces.
        shape=cq.Compound.makeCompound(planar_faces)
        representation='independent_faces'
    shape=shape.scale(1/construction_scale).translate(tuple(center))
    return shape,{'representation':representation,'degenerate_faces_skipped':skipped,
                  'construction_scale':construction_scale,
                  'sewing_tolerance_original_units':1e-7/construction_scale}

def describe(shape):
    b=shape.BoundingBox()
    return {'valid':bool(shape.isValid()),'solids':len(shape.Solids()),
            'shells':len(shape.Shells()),'faces':len(shape.Faces()),
            'bounds':[[b.xmin,b.ymin,b.zmin],[b.xmax,b.ymax,b.zmax]],
            'solid_volume':float(shape.Volume()) if shape.Solids() else None}

def export(out,validate=True):
    start=time.time();out=Path(out);out.mkdir(parents=True,exist_ok=True)
    shape,metadata=build()
    state=describe(shape)
    if not state['valid']: raise RuntimeError('Constructed BREP is invalid')
    shape.exportBrep(str(out/(PART_NAME+'.brep')))
    shape.exportStep(str(out/(PART_NAME+'.step')))
    report={**SOURCE_INFO,**metadata,'cad':state,'step_unit':'mm',
            'source_physical_unit':'unknown','coordinate_policy':'preserve original numeric coordinates',
            'code_kind':'standalone embedded faceted geometry','source_modified':False}
    if validate:
        reopened=cq.importers.importStep(str(out/(PART_NAME+'.step'))).val()
        report['step_reimport']=describe(reopened)
        if not report['step_reimport']['valid']: raise RuntimeError('Reimported STEP is invalid')
        if report['step_reimport']['faces']!=state['faces']:
            raise RuntimeError('STEP transfer changed the face count')
        error=float(np.max(np.abs(np.asarray(report['step_reimport']['bounds'])-np.asarray(state['bounds']))))
        report['roundtrip_bounds_max_error']=error
        if error>max(float(np.ptp(decode_geometry()[0],axis=0).max())*1e-5,1e-6):
            raise RuntimeError('STEP transfer changed bounding dimensions')
    report['seconds']=time.time()-start
    report['status']='SUCCESS'
    (out/(PART_NAME+'_report.json')).write_text(json.dumps(report,indent=2),encoding='utf-8')
    return report

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-directory',type=Path,default=Path(__file__).resolve().parent)
    parser.add_argument('--no-validate',action='store_true')
    args=parser.parse_args()
    print(json.dumps(export(args.output_directory,not args.no_validate)),flush=True)
