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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/423121778c4b4e849a029b8281c68bda/part_001.stl', 'relative_path': '423121778c4b4e849a029b8281c68bda/part_001.stl', 'source_sha256': 'cccc125678721202ce04e53d52a329248ce8c9dbc2dd1a4e9b3519c982d20260', 'input_faces': 294, 'input_vertices': 169, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-20.873849868774414, 38.3783073425293, -31.539154052734375], [23.560686111450195, 166.97230529785156, 16.51936149597168]]}
GEOMETRY_BASE85 = 'c$}q~3v^9a8pltBDnf1~AtK>45s6nM5=2CDTEvY6QHfU?Zb%S<yu7O6#QPZ(sb_jTg3h#BW6&y{Tc*=yRYxDRv|0zP4%Vzb%`#nd=I;OgpU&+uv(~JcthLwvf4}eB-`RVgbN1Q$COgx&agZYa9#bYcQjUyuD2gb4N{}+QsJyaxa#2O>tkMNOiUVByS@q`Oxx=!@`6zRhh0%pY6_d-Olhx>yDM``Y)#xd+%PY$ZW=))3URWe}dO=A=k%w1ID=01U*fH^a`gK<mx^!2o)c^6Xxu*-p@2@7hMg4htfhPJi^4)l0s}p>|wZdv}^IS=Suub#LIK;1e*M<1U{@z>IijfAcA8LwtcUE0r#D5$RD{6N#^JjGIhrF>}JL5XOrO2aaWr3SF%cBtA<^^zVMrwc9Gp|RY-H&&`)w|!MpuOu874@AAnSa}j0qD<zIUSI1@{P&pf8yIc;5U=N)sxr3)hYgxXWR}){+8_u(VsV`gPT9U2yVX77F^qTygTBj?*w->$o%Tv-m&209N<Ps2;$v=pUV8Zz70d3(3cQzR3*yz)yE}Y`69R$zd**H=>%@Xy)66xu7P;7Nq&3q`D0~2hsVo)IwHZ<0i(f{zE$X_nY1Ys{jAQF@$>c|UUk&8!~NR$H1fL&P9VSf)_BQVORmkhC*#9D55av%S|quvV^3V?FSpvDKQDhN^SG12%_FD4waXiDUDrV$<Z<s<3$8R>4{qKaCi}VFA@fXKEBS+RIS-{<f-x>LLh{OUvY#Crf{=gCAzW7}Jd5k9t+#`_;z!7Nb`FvJ)!E?6>%-;!id!!8=zidOLXPbJ7cU^**xaNw#{1Y{`5fM>Nk%`G%nv~PS5@*kJiQ*zp?UU-1M!Cn<#>m$Mt*mvEO7PsNy)=+V7z)WC%74QR_0k+mWuY3G2mM13B;?haWcN5&L95JW8g+&F6Kw8%>_3r=E!-t78{4_lwa~g{N5hm`j|5qmup2Gxa)j($^Cwo^YCLZxW2BNe19k9ry=eP`PBsZ9A5WFekEXf3yiBSYZB~+`XtP6(9P!PPu^E@o|iX4ym{Mb3V!`{<Tu`X2jf)=BfwoBgd>mEZm68kt+RYlAL}Z|dvT+@kA4RlVSWbgm*br_68VjGOTgV<Zj{eSYCguL*EjY7zj#sdv_H%F^uMa0|LGsf`;r_6?%L7-t`v-t&w2k6<k!1YgBwqum+^-+`Q8mW{NN8F{z8b1Khjc;_fR>ws**p*mG4E)*Y^cC4|J5z=e}gbYnw)&c|+v+U>=?a_m#t#2c!D@X~DI7r{p@By8-j2?tSH$;O5~dx$Zr(2KUQ|idmN`+Si;0*Jpf&c>P$DBZ6zI9P&9oR4M1P)knt!S8j~N{JVlq;6A!XBpesq)y*aO-_pQc8>3Dj|1DMC_p{~letq-BS>$owmG`k`R3F4g4Sxsmr2+DJO9+?GXZ37wb(@?Y^+bl8x2>Nv;JU>_<n#99GI@VPnx6w7wOaDxDw*f~zz;C44qVSqZ0d~b4A3P%IZWR7%Vl!Cy4L(7^k<PF`S=lX9o`&qL2z^NCHdZ6>5KcTJF>ym@T+qDPk&3U|3~v=eC217p9%zbf4_8nn&?-KTo2XIOnHA}KKxK{<Lt$uXn$GxRy+sBte3tNTuZtR?s_xqJ7KGP9Dhap;Mc(Q-LqOC-?*>u3vPdY)ZdmrKs(#>rVcp_Zht=Y*lGpsZO^muTm$$+&wtQWaQpkB|E94I#%+7Qw6d~B$hWLRCh8r25qKUtECIK_r)J9o;P&@g-7(7-e%m^r6-6{fKWyuUddC2NXq^eU*&N)qF1cDym-A{{$IQXsftx4uz|Es!;Km<={V;CZdg%Ir+_ruitLnh*>#b3F3EaLuyMLb13VA2}fa|(1^u~MS-k$3ZZd>Q|`E}qAeHZ4%I8fWaBab@4?cW`BOa{0s@3dSWo}b%Ga4kAZa@+Sy{nHh2`}fY&=Lg_A_V1(TI}6V5tj_PO>G>{WJp3+e{4To!w}V^XaW}u?F0}#N{@r)2x-IhrU2`JdXx16?_S2wXT&GIIbEt&mf$L>kz#rOI>~gfhJlggl?p<ra?fVwv=qYgfK1aWGOXlIeNawyto%%#u<jDw_ggg`WVSj6S_E)$L_g60NuT0N=4DGoeb8$ar2GmH-{hMy>-}-L~Ma})5!Tp}L@O^M4KNZ*2d`9DW)`$EAu62>$3-i-wv42(rBikbn_me93lj@`S;MV@r;Qmu7y9uscABFs`VXtBTub=G{hB)qHm2+|*tFJi@ZtZ(r-1q9czm=T(WH<N8`glh;@^D{mTKnpfo#56!T;o36P+kJJ_U$_N?fTH$;MP9h&3(RpEvW;>$8&*ZoeTak2i!VGsJ-Pm!Z=a`t`y(Ic=eLYI0xy|o>dXI>vuAK(+zo^@|;s(+s-M*?eqxrza(xT^0Yr3jrf&Az}@4*GSKer@4=1vQ^3`XlX#vrzxWvNo@*kJx8MtzKlTUgS9Q<132{6(DLgkRb3Vs+Qf&xC|IL^Z+%F^Yel&P^qU3GI$n~e+_AVIr!Pmi+k5A)#=>F~qxVmf|uB-Me$93J=$=zV@-z4vEO1wNDdd`Cw7te#HQ=SKnqsQg?cj=nkx11h=>xy$FY}>g~zqe1WyMg|)KjXfU{W<taJmQZmlJ{l(dsxSe`h~p^cl>3UKkSl>&-ohM?f;~FkMdvbD!93HWdibFkp0odrQrOlc+SPJc`i11E*9r#*gQv@+43B%HM#??%yXhYT5Y{NKi_|%H|D42guGvE-bcJS`vq{l_MRNqJFPkkuIjJ!K|kx|x}n?)>jA!cLto@wa$e3)Rbm%+_OE`GIMcs*n6s6lh|)|6Ql=Dm{Ujlv__OMN|C2;<;(zs%M6Z5{|L;!{ah^W(5aVI}ICW1?5xyr_;>f#s%A@qBvKIcP<lU$nd)Xpp0E^WwigDejyV38<woR#hXe-o$HKHx_BeX5;%eGC(1&d&9af?NeMd7wdUj((N`+G_XbrkIgvJ|obUU9QLWjgB=>J-Lo@$ye*J%D<P7Z+>->s0Dg&au!N7(bbMGWia2!FEyapceIBPtobO;)UMEvVnfVpJ)6I`ktpxw0oLN*qd2&@}2Z;W}9tfo9W-`Wp8D^eEKGEjQOlJFQ2FvQ!i#);dgoY@@WhHIQ3%I1uQQ5w$ithWwBR`@J}HxpcZT(^$gYnsn^q9&o)BW&=&q$UT-N`E%i?FTE;&||8rzQZ>KH%yV<6eY&Z38&h<{l*U?``pU?(v;ormf-PF73+e^NO@%zd5lL>u*w(uXM7ObA__mI_7AEdU}KE?@th^(Gk_{8s{Efn!nuB-#8o6#122W>01HRA%QLp{ZxF(S4NZ3q4B7!yj}*;9fU(}r5q9qI4H7*Y487J1s!-=01zHj#0n9!4!<qUn#OPv{`}T5~Kx)RBy9PZmktigpW*uN8F|V}i)Ss6|XmGJk5pLKxGEEW|4&fGmK#CFdl7e!*hdKAd&{bu8_+WWnSCWMPbnr;ca8dy$8eC6Gr_N7Fx?{$A8pt_;S-lUsIQwvDDvBp3dn)I;eLC5thM)WgU{OeS?EeS+oE&ZN#_8Oyd=<d!Y!F>E`YzM<@oWlv*VE}3PQu<ckf%NBJpV?~~)I0sMB7XJB+DW;z1DRZeym~Sri68h(pEupR^7xqm0rt!Knz4TLF{zYE#i^!_U*03z0Z#8{_t)(sW9QtQc&*U{$(!Yp$5&i4fehu{+`j?XnHj%N`Tur22!8j4~47FgZ$X3!`N4AoA7I@hUm~R1n%e-<dV=a7Dyv7RZ74(;q3sz3HfZEEvkp5-V%jhp-`zq=x`U}Yg%VX?B>WQ3#BF2fBQPhIXCR<3mjBF}dIrVJXQ^`c`NnSZ7d9};oHHxT<=uachp)F!ZvrJ{qC%ybnvKIb9Y@b7&L;n!^^QiMU-d?nYPG{_BvUIPUf)6GeOk1?=!`MFb37zZ}+lO{K>p}F1wlVYz9Zp-+ZM}Tm*{%<nWhXILcWR5Jkqh0AwrHm^Hir2vy9;BxFg}S~B@?A9eWG0l`c!HwrUT<dOfYRxI+6!d3+7bhIyi<})Wy`j>2s3JqwY+fldPILls+ffYU)7xoMdaM{pfR&EvIfypOfqvY6pEzvQp|c^f}22sXNl=BpXHDl|Cm~8g)PVoMghz_LLExGSX8jJ>^+X*+ebs3QrkFyMk;Zb#|stqafe^^sn)M{psQm^{aoB+gtwn`0CxV)|2a(!)$hD6LF669I_f=QD`Sdsr(bT?1v='

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
