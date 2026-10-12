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

PART_NAME = 'part_006'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/2dd2980caf87450d9ef7e42adb43f2ca/part_006.stl', 'relative_path': '2dd2980caf87450d9ef7e42adb43f2ca/part_006.stl', 'source_sha256': 'ec19c24a55ad8548e9214e9c3e61575159fafe10a8f9c07cef171757de8378b7', 'input_faces': 288, 'input_vertices': 181, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.34722214937210083, -0.36666661500930786, -0.20833325386047363], [-0.20833325386047363, -0.22777771949768066, 0.20833328366279602]]}
GEOMETRY_BASE85 = 'c$}r0dvF%j8O9e9Xa(gO5J+e@+yW7hI}y;V%Ed~>fQ=fp@}-b)i+~B`qGA@*DhSB^A}Aja!K4U@C^K|A<g<f<m)hD^JFWkGGt~asnNDY_*4p;G-~Qh1?#Xth(`M$K=Q+<V=RD^<?>X!VRLsrGFK~jNVyE%!nd9qwJC4M)PJy$wrhd(`MKuj$SFYaB$?28T<wtSPyvn;OsyaDqoySWS*EB4uFPY|+%&09Z8SR$TuBu;CU%hhSs`|w>qR+0bYp5}L!_w;2HKsjseA)QX?!-}}-Hq=5_|wf;@UE79(k|$g<}mfeSLe$kx{IEf-s?(xM9=iR@EbvY{@3p&>CTF})+9aiLGih0|EZU|{5to3;pMjW1U*x9xh?v>r+RbCd(rp(iUl7fjjOsnuIK&i7lP>y^9^*TaaeP-9|zsegID_T&vW|k$Gn}SyFbbNG}b@5^Vi9TWAFc}B&U1jm)}a#%}hSJn4o9Ac;_wY-&K9xy5A=0F1q$_>yEQC*MHd0`)*G6KOOUStRHlpudO?u2lMKn|6}suq<*p&g8aBv9cun<-J8+tO7wl7dhl9W-izv5KR$Kk+I8}N@wp`3ud8b<Ptd&uU%wmcpL$4HezdNf&BK~w@3Zb{E1y~?&Od|vICdWBNA;}kJAB%@i%-?V{m6VBD?hrwG7Bp|&OKk!9PF38s$89?(bIp~^GURRR8KX{%jxNY!57OTx`*z+)_AEsL3g%a+85QcGq(izS>uIhKN)mq)`#!3C+Pl(qNb?sepwyN_voCKBt5%i`T1!74!S+x@LU>He>zFelvchOo3GZ}@vE_ZT=MDHE<c~7J4-D;s$2g3!p*<T;U5|=B<aqnqNegB{g3f{s-8CajOr<U-^#P<cAm5AHUxFP`_jJh1l>E+cqz7y`u?`~x~rbG>L-nE*N^H>-@zASb@jVHeVFTyb1%#@x?Q)b>$&HvAL?BD@vZtdEcU+Ezsr1myUy|1LEjbR&9~}b*U{E}*2}l+pLz)Ur=I=%sw>g=wf?mZJLt#fv_#+6bJaa@HP%mfu8yjFvpq>4Tz@*22kJR(`_X;DxT&^BKZx$54ExB|ox)&0+PcSnR6XpU{jPerzw)bM{fBxw*mtUj`-O8!b=?;p`^DD%reME#>XUWPP|vpR><IRSt-I_C)pgx<TwAxt4R!phuIHZSp@U8yY+du|S^0533+k|geln<MTTfBXs)y&v&R}13(Ai(%yi~XHrh3ZCo1PnX{=;*IeH!MU^TFpFP+iXrU%%5VUC#$s`w!2J)<j+VSKU`#ztgOGP@lH0dF!B)H`TL|`ibh{-?OY^2c30PUC#}VeeK%yvm`iYY~4Q=?040}bE7CYH*7t7{A#TK@Ej-&&Yw_c|E4TI;oq~CpYVLZPpT!jPw02PqxS-I{a#J+y{fvS-?yLg{cr1k<2zsb(eJt$+#_t==iXuI+0WyC!uyxrcP!o0`wn_q?_YXfLl5(*ZA;hhXIuC5UWT61?`O-8>b4)fXSsYotDY?<|8^euPEPUt9OhZSpY8msZq_SN|9kMgZR=@keY2x@|I7F~I^4g)bHLJdzjt_F_q)z3ynkha^TE>X_rv<!#J#|(Pv<M{5ti<ew{V>!br^de-8c2to}~Nnal<;)`-P=DdQY+R?0oJiS|?Ur*}B91&avyZD5y`>!~2~zZm7%ss3P`ToA!f!);K*3HF1qo;M7(}er1z;;5Z>B|H@|Br2pzyHWSLq{@-8Oj4>YOn;1t3p9J0mp9G%@-V2`!p9WUJr@?Ol%i*`cXMwlFXTk3<k#C}_<OMtcmuG!=w-4!?g`bg(FE|*!)<lzuN5LcTaio6?I0(Mk#90%KU<<sC@xKoqfG;z#i|4y|R)?n^%vG=({9e3OfyM9!6KVXW@wygI;%zS27ycs?ZTM}&tMFPA+wipwPs<p)8*3tXO=NwFSqH%(@M;s!<Lh}mH88e#xC`tLf6l}k_<93R!XGnn5??3rRLj`nVJg@aUXF*`!C~-+O&r44Av{$xws@Ei7Qt7UcoAPO;^{fYkg+C#`S2%AG~>4!ua7adc(?=X1DCZwfUg61dYG}r!#&_gxYXPcd>z5lD#jKM<3I=Af{#Y<NqATCbpSjR;oWF=BR|S}(C)!HD(^#Euqnca(H@3Z<wIx>!N2li+QsBq`C!_DZ4o|_w&2+aFQQ$<{FV2o-Je`2?@PNc>!o}UZNY63?$DN>T@jv7TW}A2gNYgw8^NXUjqpw23iu}Y)8Iq!r{T|lDflz+t>7Z~R`^P=9=;O3nh?I;#CJ{HZQ@3-0)8WW0wH`NSP7p9p90<wp8}r_J^-H%zZJY0ek*(?cpH2s{7w^jCc2o|4ep1_v);Tb*b^>(N*G_T6fSc<K@J3u!ex$y%v*2(T=IX0^$|QBS*zWw$!`2S#G3Bp`A(j#z*A4=D%c%<Ki(byUAU~zG5j9G>v}v5VBG}!!KEHr@!N`5;Zl1$@U;U^OBuU6Ya;l~$ojafgWyoO)Y4&m9mZ2VV~dBo!GUn8!*lpLhbQ5(FJ8gdD|o75Z1FG!>;k_T54VBC;VBab@pTYSix^uxRDdJkQvav$bqY^g8AHaJ2<E|MpT3IUSMj=mvBkrkU~jmr{eFDy$5V>2#X}`n0+*UQim#)1TFKbrVFFkPKaGz~;6`{C^0gm47~$P%cPBr}d(!U7Ix6o?Tku4L52rmGugZtg9*TeEE^U`QD=(!j*c#y_v<1&Z_z2n~n7{IYv<H$4<^5>)W4)9Qpe?u~!V75&?u_s}+Jd{`kDFL*;t6mG{0X=ZE{FT@r@#l{Pr;uB7s8)~ZvlS*-vWOGTmydu{zF3eIuoN!%rh|-TmT;nA5RFM41Nzj8D0k72QP!)0Nw<@0q%h_;2wN7I0rr({v8vYO?<<|UT_~=p7r8g!Rz4SXB6WLehV&hK28n<Uxv#ZJ27v;>*13B*H|CHA4k?|FKe<FKM%5|FYx>Yo-N1Ib<9=pTKIi<y9xX@T-N6${Jw<Ob$Gg-brURrOFg`f-`DXfTxxGSzP95@c*WdKoeT2*(?9wD`^T4L#Qp<-{U_ts&gh>!Z~6)^p%rtx$hV|f$j-Ts(?82hoqqveL|kq'

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
