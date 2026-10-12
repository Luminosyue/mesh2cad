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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/963c5f8b81c045fcab90387bf3aa5143/part_000.stl', 'relative_path': '963c5f8b81c045fcab90387bf3aa5143/part_000.stl', 'source_sha256': 'a59ba54298d9814b25d0cbb2bc3839d0326ce836cd95a9d1f6b3747216d4b52a', 'input_faces': 322, 'input_vertices': 179, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.025253847241401672, -0.1857376992702484, -0.30168187618255615], [0.02526852861046791, 0.13523244857788086, -0.11936710774898529]]}
GEOMETRY_BASE85 = 'c$}r03vf(X8pn^<SRvyXGeK;7MofZu8?Q!42oXaNBIzKAS4c=0k7;ibiAR`(gmjoN#4E;YYKF9s5F&z|U5hQfRWobX4qH>k)T$X~`}^*{@9lGBs<w8!>hu5Ie@>rs`rLEBbIvW{p|xr^6WXVZxb@U}ETpjz6b(c(ksOz}Bz{I*QkR8`me&xC*r$(6Gs7argh$p8$zp}?%($c(iM}72d<V?x>+5gwot2QdBr$ejOhV$!IPyot&QFSS`bl$Q7sWZRI|cUX=Wpua=WkkN`X4_Y)Q1j__7syw)ccIo-aNRf*xhfRnNMmvvb}=Tnz1&UHDvHPQj=fR4R>Gsu{Qg*&fndVd~sshVCTOU5q4Yh7e!1bUtCGJ!|mUgn#F%N4KF6O1nj*j`8ffX_<P^~z1-awjq{FCJ@$&&yL4^#8nT<qcUe`&{Ylwb>h3#!&A-a^KR<QF-M5Ff<!jTLp5>CCaP2bJx4Zjw{(I+pncS{pLK3xW9a(-!@(aH_M82b;XQ{hyebDAK`R1k<rFyKMm1nv9&oysK{;0F(c-&TWy(QIuYV`&7XZO7=`D;8b@^}_BsFM5!EsMF`1$Nngn99CmoPVX%Zelxowf%WC>@xYbn#q;b`L6OJYKB(-=&|gZe$jkeV5H_Bc=0vYb2YC-@=@N=`L%Xm>W-Dl+b@LheX#UurM3H)Z;QD8(!JN+eUbb`8c)ml*E`wYy5LJ5hxz_I-$eQg_N@ue&#?bRgf>2N6SVT4KOW%mJo_v6$G+(04))*qhRfRv!g;<4pTBDUg^3$@K5QCp=XtijMDuMe7fbVG<si*}-Qp{*XX;nnA4^(r2KUF~pWL49T2;BbFUpScbKxi|s*uY24>`;Jvy|IX`Nee$xZjOCO7#ojXXbXx`rVcMO?{5@INYptkH`OCv(vf$Lr>4SkEhEQ*GKR?bd2h8OY)b^;c>QfJy|LF(Hr?bTC#fHmi*@B7ptwm^;7n3f5_M7|G3RtxxY`wU*mG!;`#ZuPkxtu`;yk${OJ0P<Xb&oe$Ch8Dz3ZxLNw%jWgliQm;CIPHXhFtD{e}@<wZ32v-y%+k{_SJ^Tc9_E|vU+3pfv$qe7}A|I;C-xSsQErFO0P^}pcX`@maj*P3JE`DU8;bEQ<zs|d{x@YM2c)SWc;cX{&t5-~q$_xI8dsqA|#JgtrMPdxs%o3FR9-y!uR&(Hjk+)syZHv86|FSU8N?w1mGU+kK-nfvjl44%)9jY0poMAzmr?Y=}lE_3%qd@uIxj>1xR-@NBM=V9C5+Ffz?t+P$++r3_tOa4#Gk*_zDNbUMO<mb({ewEa&wb+Aw%ajKdlHc(n&j%3`bY1d8YijG-tbua7jn47&Wm$Fqw)DHcpU%&hb^Odbl3!NB^T)QY-%ZIs<Eh=Z_xlw~zUjxw{JRR5-IaXNE{yNjllr$L-`+ox?^l;U%k?17h`eR8KY6Z|=T)iQF8Tk?%H#5WkEHt|h6eL|c7z9Am3(Dg)BTEphdG}Fdsa#Q)peXtte3;?N&aQKmS>)%O5-dBJ!apQ^F|tHYtdlN^R^jF<?*k7ntexZfi%wQx}f{Y`m5KIdz^hsk&isiamDQ0g3eS*^(gDLUS3&ubpN|(eje?+yyS84_SV+5_O;~uekxI0$D_}dROg$sVlGR5KwDm~%?;j2<8OVk)m~kH^mV*{W@UB$Tm4toan*ON*Vg-aTljt}dBf$adBe22PAdCK{t*eUG+)VA<_lNTw0h+HX0F$KE03d+|6RVC|6RVC|8-x<|GKZ_f8AH|zwRsfU-y;#ulG~Q|GKZ_f4v?h|J!P8XaBABF)tyV>rvKmm#?nly05I`y05I`y05I`y05I`_JLzFxIfB1$K|X09KF1<&(X^(`yAa@_Bpz*>~ky=hVEcr*^il0$~0fuznNcttNF@)PmFq{`O5y#_B?tg`#0(qY4g2|=YwTvlIAP>Oh^A`?5q1y+qN2+Tu#}?+B{9{t9j4mt9i-l_(=1WeYono_S?FzJnxQr(<EQd5BDoHUpXJ?zPgUUe=9$`d^O*?eC2$k*RPz9bYD3i>ArG4(tYK8q_?Y_k91!-AE~}R{?CGTv#*>_UA}rgb@}S~RQHwhsW=#u#q}%aXx&%N(Jo*3w9@ib;L$3{SI*a#fh)7Q9_2lN%U9n6=)UqEK=+mR0OmK3_wcpyUPAZX-%EtcZ($zJeUshLnZcb=Pc##=V%=WBkVzkxR{shnzUP1S3Z_T*?*H#AnA*-h)Nn>01aWU@O>l2;FKAtGFK|x;aSvz%a1Zbh1hEISKG*|X&l%mJ9ijEX9l^fPcfh2zz`o#4Pyy})_Jh^|`+++{e+TXi{s2Kd2-+4r2;2esdvFJEGiX!rdr&WEQ?M7fD}uNSg18CP1STB}CLI870&WZ)2yP5+1nmzdZ3vzYje#}<$ABk6-vv(skB54K$Aia0hl0m~BcOf35#TA%55ZHw)1dvq)4&$!K(GZI3mpKC1xG;#gQLJxp=R(@@MLH|@MQ2fXdm!6a2T{VI1C&L?F9}6kAn6Dj{=84dw@g0!O$V#VDNCL2Y5I*2wD#u1Rf@gXKWaPcm%W~cm#MP)E7JwJQ~^wJQ_R(>IWVJ4u^IIhl3-bAAlplGogdPGr@7t4&XTO9B4D}9PnIWJbQBy#Pgu<gXe+c5yZ`*?}16Zz|Fyd(5~P>Z~(Lmn6wF)v@tjU><?`Oc0H5+2;y$gcyK)W(G4014n)1g3C>vNj6DeAz0i-rd%-yf;uX#~?2IGM_#8oe6hV9(dIEeLd>UE=J`FwzJq11qE`%NflV*Sm!P^kTJDp*Jra?2nY2ZZYF>oR{6+yfOdJ4P+yct>q-VELZJptYX-UvMcK7z5^h#=nJjMdNr=wWaH_z?7S@FDO*1aT7dC^!kc1VOwMdK|nIoD4k;P6nqyPl8jx%b|tfLfnJp2;xP~SPb0(-3H!<d$R*Uoac7`@({%N(1YN7@B!#&-~(XSb4ol9dQce8GVxrfO&HHU@f>KHFmeTP95hiFxrKNpG*uY6h&U3uMHsn@I2^iJ7`cvk40Mw)awG9*=tg1WQsR-&4Z_I1#3O_;pIo_`co?)m7`dG|2zp2uYXR|a=t5zv9mK)VBw?&I#39fn!dRP#M?segV=W^Ng(eGQ?IR9@rU+xLBpwG{E{wI6crtX6FxFz?slu3luC<#u3c6AlYdvu+bd@mn2E-QV3SsOeh^Ik67RKI#cnWlxF!n0M5zqu->}`l???btl@~mr*L_7(aBaA&2G3~jgLvx`y;2iWR7rF|Z3*HA^3El_Z4_yo<-2o=e1Mdf~K@hKn=7ZOQ*Fz70*MrwV<H7OxJ?jv}pFnfLx#;UB2x2RAKX^a-WQDE;uSMHd=sIwgGj=;8+Znr@F&|920GtiZLM*^{NN0g}gFi(O&qffpLJ+rrE&#Uxw?q(oL+69N!L3oo8{gZF_R^tS!Rg=$(2u~R?ZFek?Vzo|tx$J61aTV#u@BT6?2Uf;Ac$u`=Y!{Cd}kntGojhwZ2X=~1o3ugI(R#HB6I?H0{S`;+6Fuk91ZmW`=B4u&`fY9+K9$?qj631%__8cLwhaSH_`qnJhVp5X0?9nzg8F@D;<=j|7h{nH>KAB?%&+#tV@465FT2G&a%z}c1?ajBk5O({{W(NK}`'

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
