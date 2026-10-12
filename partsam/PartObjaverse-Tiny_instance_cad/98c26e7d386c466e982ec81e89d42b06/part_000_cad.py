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

PART_NAME = 'part_000'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/98c26e7d386c466e982ec81e89d42b06/part_000.stl', 'relative_path': '98c26e7d386c466e982ec81e89d42b06/part_000.stl', 'source_sha256': 'a8bb65c4be1a47df3323c8781d5e47cfd6938c4da523915d9b754a7d3c62f5f9', 'input_faces': 293, 'input_vertices': 223, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.10510679334402084, -0.15320119261741638, -0.352876752614975], [0.15394538640975952, -0.08121884614229202, 0.08739930391311646]]}
GEOMETRY_BASE85 = 'c$}r0d2m(b8HW!<EZ9`A1VjsZRU~Xh1S&|uoLVG>APpd86SxRrUqTW=K;WwEi|nWs?M2zDh-M`ukQ@jQ7LhH1g21Hxqhn|4&`$ebt@eEPKHrz~y<BHHZD!v2J^9`5yyyM4cfuVqGm`E~apFIZIP20E)=q8VI4Y8z6lY#mPTsVMS-D+iXD?{rG>iG_N9&fs!=KL_)xeqOEJ~e}l{+yfwRb4B&*WaIokOXU=j7z&Oqe}>PR^t(<@cX3GdIikbEi(o&hme6->qBs&Y|udI)@gA{>Ptt{1U?HUzMe)S_Yl2tn?+cIsbfR0>7?Bf6I?##C_*lljDi}$mnQQ(08?eYeZ2ZKm5mKg+bpNNdD;A<q7@L)FnYbjPEWRQJ9v%_g?E*6!fD7Uzf(li}`BbX=%?lgdY;~)xMmsmml||V!qmsi1~)`ot^f4jbCQZ*U`S1ul6I%*IPUEaBN@LM|ah>E0qa+?^M|GLxu4?VKH9&b&PihwXaBYex$F@kM`yHk-lC}?aT8ceSLnkFVD{%KIcdK^883&pC2=?)h8>0=STYb{Fr&I!k6>Km-7v2U(8qgcg%Ms`FD!>YQM~$uZu6|t9?CR=jzIeMCV8P`urGQua6v$Z_ZoaE0wW%m5nZsjVt`_a?lU=`bSyJzkTym(68$m_uZr|<v~A!@9g?+N6>fhy{;oZOAEfYHaDK9@!A?|Jia$J&#K2AmK^ur`R8e?etfrIb#>79hBAJncO;?zN!B52zWC1K>mMZa2M^q8t;3MGA2~Q|e_8_HU9qen=zB~1$NR(4<JNqm`0lRW)_k3BZyk*J$y3i*@BMe&ue&(Rnr{@}>$|tY+7~_k)RIzb-SD0CeY>ppYQOxzMr+-^!T);sN5OeT@x2){3WI*6;{zp$_BV_#_cyvPzc|tUM)1R8e?xk_*kA3}iT(BV#(h`pul6Hie_id1{nftQU-!9g#fk1wr0PsjqI=}vhs8aL9*g@C?os5xS4R`wQ|-%ps(pD+wJ-0f_T@b_?-lpdj2HJ*`|_TeJmQ{eU*6L@eD=}ISKQM(eD=|-gSe;C*ZXMREAFZG<vlg)AnvKjFYc+yBkrl$7jaL`x`}&g-Yf2@sbAbv^ImaJ&3nZ?HR~zvsmUYmsmUYmsi|MwQ|Z@<{gwAr`Vq0e@}5dx?ytP3rhaix%{q&FYS!WV?kT>$M|E!Vs#yK4cEtY9aB7#=Rt9_*-yPrdWY7=k@l!e<4EoXg@jG592<8v>dOhwBZ)4?m@WbPuIT7@|o{XQera0(_@x2Z?MZx^;!a;F=+@G!dbqnIYlYPmmKZ@_JE-1C;tH&n|&JX6VyW+(BNcriS;P?o>*Xga}Rvvu!o3tXUp4zzYZ1jqQ`9tZukHzvgO}%2RL;tw%)C{S%-isd|l7GlrPd(nvu=Y1xl@{~ezwWf^ckm<Y)2;fwWB64&3a$0Wcg~G3vFoon8XNy@4^e;IcM4{S`Wc`67g0a{vgTI(k*e8o|Hc7PKmLq~qJI3PHKP8w?<IG(>W_AB9`nOpldbw)e79w5t9}PRbYXy1f214Z50_Z=yBn*$*!cCgt@`UW;Gh4KReuyents_jKQ6vIpo4vWE^UhW-u6=K{CgMUzFRlXI{y)TZ`!}C`y0ZKJle>*zuw>H$H%wKwDO1X-MZb@{SDze(?^w9_55u<`S-^A{Gy_S{YU$<|7c(KAMMNjqkY+bv@iRQsYmo5lSlL)Q>W-Z+L!&u)G7Lp$s_uY$s_uY_GSMuc|`v)c|`v)>nZw=SqIU7%zH)uG3zP%k6Aa-f6RE%f6RMD|1o()|EaIv?mzYQ+x@4$e!KtF*KhY9GhXzc`ugquQ(wQ`f9mVE`;R#fqW_qE6#d7%SM(oKr|3T>kLW+<Jc#~d>Jk0N<PrVHtiR|#W*tQTF?EXmWAcdpWAcdpW7bpjACpJ)ACo88e=@CaX>TvDZr$fz$5GM5NpU7m2z*7WO!cER@mI9ddi-}^(LViue?|M5U&9SQiqIOk2tJH{4j+b(`=OqV_)&_kf=gi!UyWOa7QxHlb?9Mu9lRAi4sV5bpr6A#;9Y19ybIos-hlVR`_MnY``{>g0gl3Nqo?4v;f<&Vd(2(&X+JLdag<Pe2)za$g7eXva6Vj&*22Z`5%e5<1U|vDuaR5n>cG2JQ;X6~f!a1vuhMtm)9^)fCwvjUhW;MD2H)hps*dGoF}xgJj~;>7!`sjk@HY58^c?&iyc?~Bcf+5cH{qMqrnuUV^L|tkiVvb!;e+s}=$G)Pa3OjbE`-a`vv4_F#j{Jvt#oDJT`Q?Y>4rdU8>m<5TW~de9{nAB9==L`^}aXILii1MEm{t*g}0zp@D})8^ep@?{2_W7{t*5c{Sy8d-iuy^uTrz($$n(}@glkqei0sl&V@(7V+qAm82>Z!DNTbX!`bKnI2&Gw4ucoMbJ2nDTzCrk)%&`lBjB#^Q|MUuDcD7)z*ESnc&Z;cevCsG!Q<eOXf8Yw9#1Hq#`vD(Q~C>dDx8C_#yyFSgr9_aq2u9R@U!SN_*r-mnhOttUqBbZFTfdS4xB@6il_UL=SLWQ6%NCr(3jy+@B~8f48}iAKBd2er^9*pYFsyT6x<E&jZT1j!~M`1a6fo3`Z7Ei9*({W4~L&e^WZ#cQ#{j;d49ZvE{0!%N2BxM(eOk<@hrywoP0{3gJ;6?&|kyz;Khtr&v!>h!`<ON=tQ^=+#j6<_lGml`EVxu8+0+em>Lw%_Tv>lCZS8<N$?nS0XzoIA{5VId|&b@O^0X0ub@L<_1sXN?aT8$&@pfi_!%?{eg^&(ItQLZPQ_>Zxa7w%LU9>-9WH|l&|7c;T!LPKOW+Fh3%CM4$+NGMTj`p>yVg*P(#?U|HdC+C-@<3$OXvsiCHOk|)%#YUCGZOPO|$}j6W)%Vgtx=*qhG-9!+X#x@E-U8dJ8@Pe}rC#uT!()NBju+(FyGcH+R$@_Hk~)xK2bzK3Do<SUuYquQ7f{o^8zYjTxu-Cw@HW$Kz;QxFNr*&wu1c5`Gfi<3w9NSDFkz$n$N{WcUF;TKVx9`Y8Mu{6q8}SdDS;9DL2K$fw3NAV&i{#Si=OkRKh;_V5q<xSP-K<}=0j@tGd;Fx-J>??aox5Al3^v>AMtAFcgp<403J8u^imwt-tSt{uO(V{AM8dl}n0FkX-SsUMyFcmnML-|t5YxCP^$AiD6m(w4A#HU%#QzYEW%@O%p66lZ2MXqb}peg8eE{wJa~!TQfa@=5!jtidPu__@qKU^6ossde=aP{Y_CL2c9ta{dE+!ZY>'

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
