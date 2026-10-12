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

PART_NAME = 'part_008'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/a45db53fa2fc4e94955e59aed66aa0c3/part_008.stl', 'relative_path': 'a45db53fa2fc4e94955e59aed66aa0c3/part_008.stl', 'source_sha256': 'cf793eecabff0483d8cab351818bc8de24d4e0049dc6ac5f25a1da992e65eaf1', 'input_faces': 192, 'input_vertices': 144, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.16532814502716064, -0.43641018867492676, -0.40556395053863525], [0.13488566875457764, 0.12282344698905945, 0.2174963802099228]]}
GEOMETRY_BASE85 = 'c$}q~2~ZVR7KU3~0exyj69ds!L0pInAR;cWT~L%LPe&8Qg+>-P1O!9eZG*-oCX^X7Zc$oCMO@0bAZRAig2rKqYhpy5sTMWS5SK8<U}DPYd+z`Ab?a13&Ah5p|JOgaZ{I$B@9op-h^$@5OW?mYLU49LTft_a5e)?|AtNDe_O!T!^e)M%b887r$fqCl&m+bRcZ{ngWC-*9;}g>3()`0j|2~PK{sE$YVoKWVwAkdBl(hH+<`0fdN>4ES^r^9_3C3}U?!mzUVo=8baiRD>{yf+i=5{<)$kf+&6KOqrp`Gc>i6`mU|4=SFmj97mz*L)AR7`%&y3I_rQ#X$@Uwyir`^QfmVXBV2QN(<GQgIRaPe<;eeov=TKYITB6U<k}&!X$;=RQ41{jc>VU(LIFj?O!FW*hSr_d4WjN0*<c^QH_wMC}jG)95%Wn%b*g-_m&W%OS_8{jsT6nd(cTFEW+BFF#8CMqHqN^kd2vy1&0|C0|T?dV$XSq&JO6?7oV8rO1=6BNtyfP2*YJgnY>>m--P-^E^o3eO*BPo_}(M#v>-vb;Xv|`P4o$hsGnVUrD|eaF2W~Cj5%4FYHeuU!KvJe6h(6^7U`yc|Ru;sUPi&;b%z){Xlt_Lw_V+{d_64S624p&*ReX)Q?c9Q+w6+AdmWKUUiv{4^;8|)M(^uYqnEA%Kk;?TzwVebozQ=9&djwmfu(QFPCV%A2uLgiEYZSyI{;Yp2w2IbUfq-{#<O?<coJskT2eUMD68(3hGB*ec=%GKYKU7udFp@ALDWQQint2>rd{}ed(d4{JN8K$d}gDqxRaP8`NIEUVV^`yZpq*KWaMp+Li?J^<g^oqs;k(_us5|FKOR9=6Q8x{T|ZI3ataZ-5;eif7W@DuL+;g{M83#kuTl)eK*~2{B@q^;)Q4Ez8XFxU-)GL_ro5Q(D}+W?vLI=^HUG|bpy@wGv(yV*)iWx9)?C7pmp)jPkH-&nO{-+FT%@c{f%BkzOteVpJ!1eG;g&cfqbccHP4Uz*HZd>&pWyN`Mc5hr2<<CUAH`rd}Y%%J`Xo7DKB*KwdlcDTzxsKPp)g;)O{m)-rm~3i`p&n<nyFfJ>Gs}_AXQVFW>%-+ErKQnC4qrNCki1W60NQ9`bec<-hp6Zq%B5#q%y5OWgv$rt2i8?WDguZt;E|T&4W0Q3J`>Q}*!Zd(*-D$>>eKFrMF+)7L)>B469>#(j^Qy#1!q?Q|cLuF<jPRmuIuJ;>KP-sSh@XQTU4!nbXuan$wY>;1%Vo}ZA<H@jX}s#N&=@8nx`ocVtD_&k}AblKH+_AhJ*F!{=uo7~sa%Uyjr`UZcFBOaBR`k%3vw?F-}sUK;F%JVj_s?^l}@?<`qqK6fx_Kn7pFFV@&-PHaue_mp*TvL0c^<6%Hj`lAxwMQPT<8jV6>v%-uQ~0gojLH9`K5yS7(bWFgbKJMaG#<fmosPBA$cv`?!v3jU%rWInio449jT;}B`VkL4qIIgZeuLKOGv8K8{i?4vD0KCeRlo7~QPt-4uD(<`l)oSEsdHU@ZA2-pcctaVGLygIHtkDt-x!lGbdBNf)l7xfwLBwtGwlb?_Yvls)_t{Vcg^$6nzMW!ZP{vn*}Q!{aJ&5_^IQr!O}=$q$UVF5w7+B>i9g!Ocdke6PL#=a&IhNj2r1-S*R{CIJBRt!eLzl)Cf~Ym$RFJ&|Al>~(RQk1qye}2cnaR3`_jMPL%ww%(`xsp`pLTQ$<kC_SE*Y~`=`^l?w?{v-QCoWWq(%h%_HBspQ~9X$d?OR@%LY2QK91j=ecirUr62+<Xhh_Le2y3Ti!?d;u`Xu?=S7>V#>3&uW&E<$dB{=DEt&h^_2B}Dt7&ud^M=b{Qlj)gX%l$`&xbX0QuJUyIOJXkn6m4)&uHS-;l4)%{A2zN{Dut#%ZZHq$g#EUFVOpKG9El<WZh2^^BU7pJ$pUsDG63Lh{wW{MA%PJ@YMflonA<{tNY3v2=vmTk1Du(VZi%d3M%&YP4@Yjc1Ste;-#};_JO#9QiNQjklBY`MNjPnM&dV^2HT9P4%kNx7MqQZ#l2)Ep@M2VLM9KwbaR~yGp*b-qzRVldt5h<@-yCZ515{m630)+r{=hj?s85b-ohm#_O7mUHCd*;Gnuosk}wL5L!X|wUFsezIt}PMt`?_N678#o}hj#-yNz?ee$IvkNLd6_H-?sf53-)>-URre<1n7><}7{R_0M+cbL8&13lUwQQX<5jv%-jUyq5gE}xFfWIw0A{L^t-@PGH|*eme={dCMS#<0qWmC!}t2qU@}F#y5%P3WuOH^D8SO~5U{jiGOV8-sn&X9BJh0Zv3Po(G)^o(Fy(x&-__I2}40oDQA{odBK)9s=zTW*Pz>0`3X*0sCP5jJq4rmd#rP<7NoPuOk@yAsF{SFz#wZZ)hI`<1lDja9dn24B8hQ2JUCXSR>vs;w=Q@p$Nuy1mj5v#_`axV5V<_<H6&g{lNWj-Ej!Ulac4i$m?YI6A*oo<Nn|fXm@Z3*as?teZY;O&A`o&U+27H+yd$+JfDY***qNpm7soLKRgc!Y6shqBMCYaEP)dcjGgn5X$EvAI0KvvodlkQ{3b)kfyW_t$q2@&F8NJ`E&->47eX_@891NupNtr7L`MYUc1DahLN;O+^j+{Quwq205v`2~LNNA*HU)cwZP1or8`ull4eSN(3>^mU3?7VNJOvsDo&sI~eGj|<oC#IH3hpHn!FUc-2G0S<8Zi(W4wb<&@)eF?9BIS|Xf$*@I2xP+odr$-&xb1D`QS9@d*C#13^WcL10D_?1|Ei-4o5H!hPDI;gIhtHf?I)`LtBHJgWEtu!EM03kcVE#K`;1`h*0E=X%KiIG!PmD4g|jj^#(JwfnNi=L%qQ6;8&oX!LNYZLkEM~g9jlPCqbuxlfa9i3&4xPE1;QRrgOlxjc^nAk7*s@`HyieXkG9aBLa-@g*F5)H)4hn%MgsGLq~$AgQF0PI~d^!^@olG`-4Y8XMjh6r$Lv4r-45(;v?wC(B<Hd!K<Omz#l@FLYIM;f~P{KgQtQW&?s;e?!kdz+{xuWJ0Tc1GNJ*rKGYLj56b@C+!0yJ&8zl*`ltWrKZQLY(|-h5&oq~Pu4nc$`g&FbIwI?`>l+iojW&SCta1|m4fLSf)B'

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
