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

PART_NAME = 'part_004'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/aa1a732d4fdc44e0a20cee312a929d77/part_004.stl', 'relative_path': 'aa1a732d4fdc44e0a20cee312a929d77/part_004.stl', 'source_sha256': '65ebfe6742dd97b9c9c16e525ae5155a352804d01fc3e3e13cab11c5cb679cfa', 'input_faces': 220, 'input_vertices': 219, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.1204100102186203, -0.18636180460453033, -0.1504911184310913], [0.1871122568845749, -0.024121858179569244, 0.40194350481033325]]}
GEOMETRY_BASE85 = 'c$}r03s6<Z8OM)+&!og>j9TlJnjmV7;Dbnw9;@*IQ9%U_qF%s@LFFN+5rud)LJdZ%&BGWKt{N4L2r8f=!T|&m6BQr$N|U*5$4qU<nxt)-)Qs&u{(ExHvYqL)%zX3z-{0Ncv*+9Ip0n;48R6^KUE_cKwYC0(u6O96X*3?!x@)Uk87q<#U715u)3e%Wof)TpLf@JmJuUL(Hrgs}ZQvqTW@1KQm?LmZ(({2s9Dzw`87ng4Qx~RXEOJpkDSla|i}1`>;?rH^^T3ec(L)@=gN8VA9RK5ACo%<N*tME*bS~e!&ejrfM}<^Sbq4>LanH9c)%3GA`&-8KkjH8%cmK1IwbvIPu2OOLw3u?LM#v1twZ8?iag3P!N~Xg%bN=uiZ=ZPQw2B+yc_)~Te89N#>zp&}dULL_ar9mN4BLFBd~uxV?s<$m9^7N|bI++~?X^9*hV_0m=Z#Y;u1|W6kCRxy`R9Y#b={kCua8r3ebi<<KOexkpIgb@RoiUbxuq-P-oLL^^N-%P^XwnkeL2gr)ZBlEjk_D~D%+b}YVRq(T&0?ir=W>(QoJ^9Os(SWcW+Sh{#$L_TT{WfCwvp*T0tFefBy}}jpzinUe1DhhP4je3!6?U`J@cCUfyl@`MQ_iId2_baBtlq#vOjS*Hqk7wYkO0_0Z0Ydq3TLRms2Jc*Dw#?Y)~=e*6z!QE{Ve$xSQwgf*XIb&~(vW)*jj7;(#X-Qh1ZuyGcIHmkViylrdmtXN*h_)}SzRon=fecQ^lt&eJ0ez*MYl8S5J724W+FMh@AVb{@1Dy}a-Z6Ck<50%RC!R7I_n~#pG=I^b%d{mVO!CU2F=j%nPJPR)8*%%YMU%8Ip@;YkM+ZU?p#N<+)xW5a3UsZ4Jq!aI1>(&$4qmGTUyNIo?9@pGr<KsJVUbN_jl^gye>)Cx3d}-s3fMB-np3tb9R_@I2V6fkX%VXnO%U$;S@@$%In~(Ri6a05K_ys$UOK04<ZJ>>NzUs@zDeGy!uWW-o-<)r@wcl4$|0)&Nqt3DSgv0-P`#5)(GwvMvM>|jX;go9r?g6WhvAj73UA4`B-L6u0Ur!#faid#62^&8_XU`31VPBrl`z~JRvufD;(OWp0Ul;E?eR376Ux#Nt9|zAjJ@PN?{pj(e@ciSwW=st~!Fd)RU%bCw>dN1zp7lHr?HBXk?}EeZ{v3O^@b>Nc@!xwwD$9qycMqRWhn<|S45(3Y_q<Cd+5Gp`@p<}v%<93t$cN8&-{*Xu9g2DT<ulJJ`P@hBckKR0=XzD$np~<|!R5LYT&`Qe<+?S;m+Dq<xo%A^)ve%i-O60lp?O`Yo=q;*v*2<)o9(4~Hn~*Kg3I-6-j`I*W}c;b*7kSd<M?K>eCn=n{vO^RT5qeLm{`7l`(P!{zfTaa6IU2(?>JCcZ>!Ig>D4MO_LGi-pYid1zo}*8U?1o`=-XheXFX+XwTc_F{=~*{9~#NH;d7OZqpiuWRdGFj6dPYFn$=*d^VGa*71yFe`1`6TzJbp_na@A&_w4uLDO%ZJoxk>KRgH@43zFEnd5hND=O6nn8%Hb7ZLsFwo!<Mbl8b$8@%9F5{`J^=Hjblshi(4G#L_wy*V8-keRuHz&fAUWd7ikZPQ{J1FRQKG>odc!a>wB-d_H&%cqZ^X$y`reV{31&i{Kx2JIC60ywB&c^ouiA?$*L<t=xHY3ghyAPjGp^Cv)-s6<pr$wc>b>3oh^XWG?mzg3J3onTvghd0lD0Cv&mS5nSHy$z1IB%)Cj@RkOYHToqj2AIe<p-^}}xo|9&K={aexi?pAVx!6yd<4F5SnalH$_mk%M(tc9rt@14GCuJ_Lqr9J#xm+jmezFyp>QLTKnq1mX>PHsx>vn9*-m_XV{+%lLzk2cK*!VMslB2z+q{Q|+)smJ}S-JT;9k<X>anas=^Z_3S&j%y%!f7iP&j-Qv(msuhi|0~&f{lyklD@XGR>ehoXK4^0M?4SLY^_!D_%PPqQ<h`nTEv6~759wo#lJtc#WqhZBDg`t9b?<t+KYJ#?ml+9(Uza759^hD&AwVIH}eMWIsUNGx?cKf9~&3zBDhvQxyf25?v>#+Hja7_+)?pPlWqKrt!J&=93R|WQNp-*pNjpYR(X+eb03@Dj_)%oTbiu*tEYccZRO^B1l*`>bKaU~@qQOv<XLdX$u8%u>u97T@cm%KUm2Ire`GGse@rf&|HxdN{|GLh|Fq&b|1r6A{?m%%JV$W({HGO{+RNuZCYR2C1eec$T5+8J2yQ$7iL{-fZqHj1-rPykXmr%NYf15zBUB3MpHTG?YVwHx?g%wx*#CQk`Z}v^O{<2UhF?jdg2Y<r33wk8vq`jt&Vi?WUqgSYC*fC<I7%WD`XM~M{ZtY^g)WEpBN0QQ4RjVf)%7H1LN~&%Be8+RDd-va6cV{4mO?kcN0P`U5e3bG-+*>!pf&J)NTh3YA-Sf&uOZPy;#FuPJnj1{^rvdT&n0n~#4>0JJZ*CX?Woqn$Kc*(LD$1aVa_w4S@5)PDf&}A2cJRWIEhuzO8EB3haWTsp7uS4{!~AL&%x&`XeoSOTw^+P6+CTIj{a0Hz^CJ$Q=qx<?U17m&}H!DnDYhbC-6(LW--up+K+WZ^Q1v%!dK${KY@M>A59_;*UZD(P~Q>rY7bosPy3dkKh^W_Y51H0Jq|wud71`Y0Z-eMpg+|H_-x#B4)hrObmTS?nhjrqIX6J-;OTXaAm2xj>vZIl=JqjY8vJ40e;u?Ip5|{O^0X1(MI)#5J6~utd>-1>LeIi4!(7v#W$<*KeUOtCm}4LGU61}$tKe5*EwiEJ@V=NsJLp_^+IJoLQ#}Pw*P;~HEJco1AQyCAeW4lfy-7Spq8Ebtp3o=Zd&2jCc8Bi)-woOoo@!_KZtz{8{_tJkpMX9N{{;L`NZcWDo5U^XP54{zH=r%>H{h>Bufbo3zlxx~8F~et>Sg$5_)E}>@R#5}CGjkYT_grWcfb#Z4}!i09|Ru=-3}iJ|1|X1@K3}49J&R*KZ(sG`a$1-?+5=g=q7jviF^_P&^O@&;0Hjr!ViFd2D%OY8Tf(F-@p%q9|V0Heh~Z+=zH)(;D<tY!w-cY1}%UePGT>Kk<k6{BjH1#2jD~DM?(+6kA@F}7Qu(X{{mVJ|2&C<Bt}6$fFA`v0=f@=1bhh810Mn(3@wBYhJOya2mU$uXQ8{`-zD)5iTTht`1kQ$B6L3dPJEXDO@xmi5l$i*`U<>G;zjg-5$&lThwtK`^WmqEm`oxG>Vkg>*H{8gh96Jjmn0TI7s8LlHReI%;OUr?FfP?a@KbS(#n2`2bj%4Dm#P!~1zaN*IuD+<nTU2&<Kf4k&&$wQ_{fMhKHYu)(|;-W@y|_P)VBX%AosLyqpdwBk+IB8b!0?a`kW^lQy;d8jB?OV{|4*|R8a'

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
