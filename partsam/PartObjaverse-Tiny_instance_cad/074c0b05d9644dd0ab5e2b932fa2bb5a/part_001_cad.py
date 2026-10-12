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

PART_NAME = 'part_001'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/074c0b05d9644dd0ab5e2b932fa2bb5a/part_001.stl', 'relative_path': '074c0b05d9644dd0ab5e2b932fa2bb5a/part_001.stl', 'source_sha256': '71e532cbeec72bb5157bc0338bcf78d4f84ab5bd67fc2c9c30db53d639589f43', 'input_faces': 284, 'input_vertices': 224, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.27173930406570435, 0.2764451503753662, 0.1783679723739624], [0.28457629680633545, 0.353137344121933, 0.25560230016708374]]}
GEOMETRY_BASE85 = 'c$}@82~<_p8pk(^Q3_6x<y0q9!N8deN3MookaRPYLDTEN_!J2gMI0`J@)W1kN=59d4Puc=D43F0F%bb#LCw^-R_~?Hq15NHR)f!dzQ5<(@2vOMdh4xs*ShQf^W%TN{q23u+55Y9X%1`d>M7{;tjJ4F+irbA2>Eswo+3Rqb#~&k*tFisDH$%Jts0lFhq^9&+!%ATi%1ul-qT~#rloohR=kJC1$g@@-f^>1XQxg{o;)jcdaR5GPnnSx`yif{FeN4S!M}a__xJZx2K4k(7ApVatL1|dOueR`3X~;XxqMoxJ!)B1pi|r)_Gp7t%c@B%uH5gV#udLo+}|vk;#nP8+<GTljXO&3A7y!V7OQdb(=`@%{P{Kc-M(dU`!?4`HDCBy?$7G0#zkc#i(AG_RO6P|^E`ejPmSAN_<`5+eTf=Z-0!luE%Xw_ueM_IavXW&j9S<GK776%`lxXwFpRH{?|3zC9g)V@vpQ3aI~r`<-+UFtZ=bGb@z38=<Ce$<UXR#K@sA3b-&T1@joUi6I>zdJ?lk%LO=Et`-!7|h(|{1>w|BWk^_aW!{MGkqzBlriU%BpaR{i_>?@qA%DV^20J*SrEAL&E>=QcCHeYw9HSMGUMvpoJLivRH%^PBv_DE|%%^DC+2$ZvOLep|=MYFvcwVt(6i@f6=*TF2tPDQetNB960hE9R<k)3B-BKW7o;c{+mm9htdm+*0Ae{Fal;sLuQ%?w_=Z;w5FZ>^crvOY7z@YS_5L-=_RY7Umag-c{q)nn>oiblynwn)oR5Tk0q-d_GhC!o7#OUx<+1G*0h}EN*u%q3iZ*4vQ-rKBslc_pf!1TdwZG{o>2~*6Za|uh$CZx9&MW^M1eaI2$+e5XEc0<M}rnrExbd;{GkQRDVD~9g8P5(7Zc7&;3`vp?Pi3XMU^S_f&u7xoYRQsr7Zr?|zB-#ooJA=R0}KZ~yH+UFTxo6V7qlotBg@dNA|bmUSSVJeT>cr@Sa0^Ybz0FY7~k`XKX*p~F;l94cadduSM~U!rS0ThCT8^!FC=+&?mr^86OW{8rZty8eYeydLv1@(<2pe#Lte>8_hqERW@5`rNs4UQf3QTA%!V%&&yiQ~vC0ydJ}Or`2=ipY-?T?kCy24Cmm(xZ{t`YTTZ$Fu$XHUo~!feGv1TrUlV?cfKFbk8{($qa&a1rI{2TXkvcjd8*B~-v%{q`XG$?jpwX3-_S}mZfzUE>o=Ug+I>=Wll=3ddHsfSS-UQ4JE?Jd^#q>Za9(TkdNY{fuH0`t$F+I&Or>$XBe~yjzH8$yETnn{nECn`&V8*O|6}Ag2Q$C1AJE3_ew*r#9K`2q=o7SYpXf~I?Aty0^)>VlTK<b8)wuYf17CkbU!jfbn@Ik}E_}X*enY#yKd+>Ipyo7tULN)vVsQh{Z|FC)^)d7tTAnt%-_YiTe!~$H!u^JRL(6aIH?%xo^L|6~PvrfEzF$$lq5NLJ{KkGm%cJmqLmT%g-fw8@Z0I+%b!)-<4J|+V4ePp6c3v3!4edTD;{Ar^H}o6YxQ2d1tKZOXXnsS#p{<WM?>Dq@4gH3;4hwj{q50i-zoFG*>^D}>xn<4CqPng%vbe(|oA%eM8+p8S4%K_JO)bl_DVOSMJ(=g<yp;U&Lz!Rnq;twv)Q$OtX$6hDCYR^0TTS!mf9<$)+<s~ueeSIa=C@cjknSj9ep_rI<sWyK=fAv-;@O$ZuQcwUJbQfWoa3fpyGYvvbAQ*pRM%7s^IOyCJhi8{=k=JrqWW8}<NlO7%I|Pgvw1Z?Oa6pP=6AR^QNF{wnP17cLZ5s27V}$1-==!HF5&s-|Bm{*oM7=bZgdVNOyK@I?dTjY4Pt(4kFNB+b(=r)TMziqIe0UX`?va2o=)wUUmP~kxnG&j{r$$!IsOa!v4_{?BAxq|{yUjpIU7gy3~OY5ORL#b&$T1mpO8iVN&A^!5v!@5CoeL;{orOA*Z)K2w|}vd{DD6)zv)sr^$$O;XMXGBRpej(C!g;dXUM-LkJnTGJ^4>PR?qwqx2c}!Ma*xzA?Td-Y{&ezO>NY;$&|tCAMiB!eLcC~;Ya<0?>t`r$|2<M@HqGP2&KMaWG2slFpBd0;lcdMsCde=B%Ay9&Y?b}+?CJQGne{=+LhcNx|Z_Ky2sZu+D85-3;F#J@hSPe{?6|Q&jZxA4F8O;|0mVt|K%jVAG(|)e^M3q5C4Ju9m|<t1l*$a@Ae(9XKYJ4uh$CpTsR`Vs2_;;VsZP8UKB5lWceM+AnJ>@g>e5<LDWCo?92Td!)e?*v-tB^8%6N|H@-dvQz^ek0e{}zW>BBA{u{Rch<0<R&YQ=$zic7pN&lGdhd(YM|L9-&I@qYcax`V|{rTQ{)bGpoTXC*{<{J{s>xtM#<8HMuzcqLV^?{9Tc|C`VsUDYi`F>tiLis;E&(0Uq_%iBOzdFJ5$LyzZyKQBD<;s_o=cpSyA5GV&4;01m%x|B2gywr;1oPWh9;Nz6_u}Vci(}-EU%>Nss-|&g-sb228j9PJ%G9`Z@j$9`d3SnF1CQ1On%S?n|G1EBKItKZd_N{UMcfpppKfJPz8>no|LHc-|G)d`HsJs9)2(oM@D9aW@+;70;8(!m(B|N9uo>zKHiO4PTY$%cBcP9fBf#UKZs76YDCnc$C~yq)F>nlcBD5uVB6t$C6?hWZ0(A#lz*C_f;Hlv0(AMDT;5cX-a2z-R+7_GuPJ*@vCxK@`J;5`;$<PkqWN-@fDR2rn71{}$3Z4z^0-g;{hdvEX2hW2l;CbNrP%rR&@B(Nz@B;86Xb<oruodb9wt};v&x5nUxlliFE_f-_7rYd_1lkk41e^o)2IqjYpxwb);Kk7Az>C2Pq0fRBf-|AdfHT1v(5~PN@LXtT@Lcd5Xh-lIa2oVUa2ohc=o8>K!Ly)`gJ*$fLfe67g8u?d1k3kV_`B39Cw~?4Nv(FuUybpl);QHugL<XbIn`f>`AMyJnr}VUL+UA~^*M$0liJ|4o())Usb`$l{|v5=)N@YP>m079)bmc)_dKq@)C)qtA0+2MFA4qrk-P-@t<di`$xERZg?@iZ&V_y>^!r(IHuP(u-~W=W(6d5+UL-GqHVXaulDq(VTIkQC<oVE(LVtcG&x4*2`tvS19a<~&{Xz0<=y9R%Cz4a4$ArHBNKSzs75aW9IT?CH==+=G8PH0h?}w6;pofLNe@ae(+J(N~N{)kmDfInW@^t6{q3`FCr$WCF`u;E30xcK%c_Dccbg$6Q7s(T$r9wZCB*#EYgnoWWj)HzB^z%;gc<84>KOZGWKtB=sc`A7<bf?hIU&&_Z4xyjdlEa}N3jKVS{0j7aq4xulL!sM*-akkljkn}rs0|zp4uWn02Z2XIH-krlP0&qX6L>gu19&)iDD)lhQ1D>rdhlRy0CX)l06Y-720Re#4_yWJ2lt1r0QU#?g)Rs81^0&j72F%#3z`S+1?~e~2JQpy2h9if0}p_%1P=he09_4!0sJELE%1xrLC|&JLEs_Kx4}ce!=Ueihk*m38^M9#5zqqg2=GhLLhwuAQPB6mqrf51t>6&w%h2uMm%(As55QsIG0=~|W5BOMi@>jfUxR)OehvIOv>5z4cpP*WcpNwqx*Hq`j)r~?js{PF?g38#zX2@+zX6^M-3Oiwo&wzuo&uf*tpHC0$3hQ+W5Mx)`UR<npa;Q+z)jE!a0SL_g6;$FL#<8FJ>Wf<a}#tocsJIr30e#;#x-by7J-X!Et{YpfTeB+OWg{V`W{$nAy{ew*c|54%(MA_`ma3t%PPNMvH#d({3QPx>HNtrALP=$RGPzD$nQ)KzL+(mMoV_0;$H$;t;z'

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
