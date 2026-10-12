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

PART_NAME = 'part_014'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/63695230beb44ae68650bdd4d914917f/part_014.stl', 'relative_path': '63695230beb44ae68650bdd4d914917f/part_014.stl', 'source_sha256': '5c94c034f06960db759d8231c9aee3a92e7bdb59b077b3aabc71a1b88c213d73', 'input_faces': 198, 'input_vertices': 141, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.0315241664648056, 0.418575644493103, -0.024050526320934296], [0.0320286750793457, 0.4861069321632385, 0.1503557562828064]]}
GEOMETRY_BASE85 = 'c$}q~33QEj8pgkn*g{1Gt@R>Yk|1lFR>UQ?l#qsqEM!j;OT>*tLewXbL{QSk5^K|1MrgE_v9!vqnpT(Tf)=F`L#0(@)G!n=_y0am#?73WbLPz4bKdj(?vwYv|M&YZ-*+z|qZ`{hYj}0n>TZASbFh`Bsc5M=YgtL=*{KOh8U54JbL=!H@ztwdOUH%<heX(ES=u~fVp2we+4!Qt=%4IobT=52XPRf5<I-YgniG?hKO$~=Mv~RfNQp~NvcB)*>Er2c@b2qwm~Z$WUoEUH=(Rn|k6P98g+tX~tC~u~w<*<6PTrt=Q*3APEl2)bq0~^>ZI$x1`R6XG_pyC8>{6;#d|Rq~JtaVV{mTQDqOF#$kown;ieK*2akuy`9?K*@^Dgoq4%j0)?)(y|KX0!1hJjhgH+L3aU-FFfqaX6wE9$y2U+V9DB>9%L>-I@M)j!M^-~A%$o9_Nm{7}bSxvtmt!@t)S`S~}qr2Zm%)ZbfPCVi|tmMQv|U6NnzGiATz|DHKR{F&=e=lM+s#UGnAUB>-#8T>C!A>Z%bG^zifKz!2&H_*?CC6SVUU@G$e<b*m0-;0p?#fRW`iIe%#avee?|JMPSpNLzBB;PVNNa{L0gLyc!5&mCuL*(;q>wXlibAMla`?2AY|M0l@rcZ``VC!qE)?(a_iHl_1QOPmlKiVL^)_HZ2`0cafWxTp+@VBi?7eCrPQ9j?TH~iMCOT<rqG*$Am4$HWfaT>;r>ys{h_+=sgh<~x<m(83ddDmj$J1<EUztcAHwE?;4^TS!_Gd40q{E`0fkEUVX&K;gDep(CEdEaTCsQ1MzsXuI$^keY6fqu$P&5?deO2x1KyyS2L|Aj~5Yg_8DUwgF37XPdZ>igxUi57b1O8u9E;h&BVm;8c+1>!q2g?}M`KKf~+i+`X3^%LKEU9RIo_l4po3_-r@-!TujjQR5SHzTmV_nL2#zfUO=Uwd!|^PF6}2)>~}@@_wkIu-uXpZ@d20?f}b$uI9#h;iGl7vEwWh5BC27aq0owY+wyGv>`##IL%Je8*1kqg|$BU$-k1|Lr1N*YT3IqR(ZDZyM-``S0=aR`GwX6<_;c1@d=1cvY@9piMEx%SQh4n2qxO-E{FSQ}!W0;j)}(?aV&-3HRZT&y#i1CUsmU<8J<1{MeL<a=ltWApDQ-Ul9G}yv5en{bpd?-<Fl5&feFMKLqo(y?P7I_0!8G|JtWgM?W3(k@&u5@lBp5(a+&`WW6<q<H*1D*$<-U13nhtquC14XFo^&qA#)U%{|4}Jw48gzIy7I_zxq*H%$l<zx@0A4SYQ^`2zN58~7Vvfqx`H@+~Ew!XJ`}aSyE#-&C3eKfeTilS=Wc$FFGMo1$)@j%z%8<0klbJ76BNV&U&Pjd7dYLH(8^;NPx=@A4V^)ZGny%jvD?|6z>Gr(R_!k-Sa@oKxr8o$~iRM)CEiLacB7x#;CDzNOg}sZ$=l(_-uE!-6r-EuV^!{ZkeqzLu1R>)Kv~e(L?DN6^ot(3fQYpPz<)5^Jz7wI<2eOV?xEecm`n?Gr0-{yv0nd{^>gw?-iU`dQQ&QiwXOXJg!>Rp>LPxr}RR+ZX<dtLSIzFw9%o4)|VwL!C<n=yOjt_F>&{obPdASeK8!f`26qe%(UUi87<k{!IAicA|gZ0NM9ic)s|Su<odzZjb)IScCj6tKeU7NB!1&an8Ifn9t2akJ<W`=rG)`o*E?QNZ)ONf2keTr8;AvsAHY@rqcze;~kB0D;?j!y37z?t4cuq=Z3;JJ;r=qvV&hSQGC-^p}gOEPZYg53;9QPVqJp0k)OF8`5_lj=WJ7qTYepW<w(qD>@MujpPH6Rf4Q~j=a(z+3)_`qozt*Cr**~t?AsIhjlRLW1zeTqsP>?5DXwQV&RwrA$83F5Q~>&aujvla$}Pw*%)|4&IKD{UfBXr2hdG$%-hOf))*JU*DLQf<&QZlpyuaIOmE=9}!Mc}^-fin^KLzsKX`990u^9O&zPL{oSN#F!{s-~(6TY~v3H#>Zyt%KI{(J|c{+Sxw_j{MGwmpxQ=u~{Z`>)9VXdUVd%8}=yUh>i!+kK)Nzm@Z)_umX(zk~dm9(WGcoD|=*!431XVI$Vt^``i`(-G|d2|lme`j&;qaqgUJ-jlqQWo0;bKZ+mwpu;=z{(u?t>hZhy)q!tdzKV13+&g2B^?E$)E%bX*d{d7M^m(}k_t}ef>qNarN<Rjl;`Ne$yQld2w*yeWvIW+4wI}?PE4cq(x`uJz$Q9o*{cSwg9(!Y-czh?mso4bhgBIbs+zc4!^Of-PV^*SXj}2016V9*6Wi0lsM;iQ7%O&3svH;J=&3WRR;({=5!|!6;ydm=3wiI~6ukw;Qdg!Q)*av~|H`#5+btT|A|4R(cohb{yQ@;NU{*tTke`_iIYdL4&pV$ijJFhLazNLB)t}D|E-#1!+g7KGM#`#*)QtE3?$#NYQ#~hsBgZ<wf9Ma%d-@4m1-<)V}9myKat-tz`<7|HNDO1{@{`;SNsXqVRPreuY{@<T`UDZ~yh9@<ataLQllN?QrB`cjxPNtfvv&l*ql9kRQo5}O33&~0g$gfiKs0HL=>QZU}S!q65=@Rl%av?RJyokDhp?EGepR6>8JeNF+nn_lgPF9*qo<<F)rjnKVla;<m4k!Ci{mDxEk^57P)P7{8oybOV7lz^v48@Mru4G5@v(z4BrJm$x$?nu>vO76gd$JFLsb+F8c_wu}c_ul_X1%khdE_i|E<<sV_GBLvQJ0d7$jhjO<YnZ=Hfz6_x`4cxtTPnPp=Oh(Q!}X9<ZR|;Q0J1<s57W@$w}0y)VXA(v&i*(Xeu?FJeBNA^&yY5Mv683s8M94L1d-Rll{nE)FAQzs+%=jt<jh4M(#y*CHJIuW+--{x{_VU_4`wCe}*fs!H4WibtAj6A75$^*_T{DCqbOoB=QVu6gi6XGJ}!A^+_XVFjBbA)5)W#<H+MUccU1JJ*Zw}4{{%yIqgGrBljWqruHKDCU>)$-)_{-<Zk3=7>e6a+mjus9jNWe?U~ns>Oywm+SK1G6s!A3pf!eCV>m<c5QgGGR1<k1HGpa&o0u2CP&|U6co;R19LVv8Q3sPJTO-aI6RDBpm#HDtNb*=}C^eEii5f$VBuBDt3^ksdKux5^ljE6}$WZ(WL-7>qWb$P8H-({iJVWsqo9h`v4Iz&q*Ux_l=cfKThf_ms)+>~AH<%n|bNyk|7;^n}hEXHPVdM!6#Urip0`)nD;+LoqWP>$2YU-;ILUB8W;-{(3WTkD%N?Vbgtnrkl{wZC3v4S?UMpLQ-!`>Q=tYJs3e<^OvP~3!SPqydhn=ll&pf)2n<G3vtid(DsA8psjx$%Gcr~fA}T{YF<KLY;slMTN<+J5q`wbnnsOoohhXo8DsBoB)F>cndQ06PfGlK'

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
