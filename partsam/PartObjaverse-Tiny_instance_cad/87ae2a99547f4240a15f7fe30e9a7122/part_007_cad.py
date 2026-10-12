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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/87ae2a99547f4240a15f7fe30e9a7122/part_007.stl', 'relative_path': '87ae2a99547f4240a15f7fe30e9a7122/part_007.stl', 'source_sha256': '276c55f620ee6dbf793acc2d168682a1214cadef4faae696349ef4dad2811d9d', 'input_faces': 320, 'input_vertices': 236, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.2945733964443207, -0.23224572837352753, -0.23010101914405823], [0.29239019751548767, 0.32011884450912476, 0.37740638852119446]]}
GEOMETRY_BASE85 = 'c$}qL2~-tF7HvT#E|U;7Cdz2qxDZ9updunlyC!N>TyTpf9~Im|L2);&afwkQ!F?m&fD&*41X&fDeGvpj+?OBJ7@`xMQ8UpbI$f`BGfng7oH;Z9oI3Z`eXm}<dcV55`06#>wr(?lf7%HDSRK0E+*}Y?Yb-Pqf_(!Q&7STX)Wv_nvO0o2>FlH7_L1Hrye8EVf`t{1Gkk-l2Rgcojvjt)j-5qEzkt9+fj<791q9CUW%>}Gc|pFa9yH5mfv?(s-=({2XR&+7&f+TZfBZC5Q!ov?b|HhMG}<lAll9vd9Al^)SjF{U{YV!I+?TMvQWQkG68kWh>0;*|#~I2`-yz-N&@zww7sOAc@dXRcGZel(OL3IxQL(HqCiEiR?ER>i;-n{29E+t1>9XGvilcm<d7Sl4eeRY~{Ee<96yK>VknB%?E+u<mI_dKLxJdFlxR!LmG~_h-zZaKIem~wgNBJMQ%k$ja;WXv5;ak!rORMutmu9)0AiVzu>9YT5(uJXc8yT95e=VkXpAS7p^R6yTqPXGfNSD_g=KjN64^e;Liz331K*~q@t<?pxPYNX6{7a*Js>5rcG*0Q@M7p%V!t<$Y6;FNVqC$$(KZ(XG^CKuvWt%tYmLKo&xbI}A>UFvIpInc996~tdNdeVoYXI{1FVpLm_X|mv>e*+~x&}LuE}oIfDQ=Wawx>>4;^&es4{W)Y;;wj-NBM5NPWfAYX+iNc-TbmC<s(nXNuxTp*iX7?{0xdC^zT&Qsng|d2S}GXC^6I*=jRgoo}_x3{Gu<?_tL5t>E<jq@)v`ypVjMv63pY2-b|$Ng>^|+Mh>O=D~oI?j-{V_4&~p%nfy&oRa9po=0P^aX?>N}qd4rLbx3dD;kx@mUWZTiQvK!drld<No^w5;GK<Dl?#UwkU{^jqE1BvqK6NBrIMA1`C)$JRAiv0???H0R=lQIAm-f5Ts}t>OWz+?#gQarYC9;1Qc82N@G>6tDHN99taYBdCewW-T`Mh5>ilKEa??$?i`(7#e&Fw<-ONSrR_am%I45NAS?wqB%g;$U+zuuSchv0j(UTJC}>C%RW-;sazaq^eEE~V1Gdh|Q_TT1)U{t;VmBVBe0=K1u0Nc+X~<;4^lU%ry^5U;$VItZSjq|1M{Azf*^o4yCJvQ8Z7Q>TT~d{2T(X#G3<>AW%Tx<&O7n`d06d8Rp%Zb=EI`j~T{@w$!s=>+Mc`%oQ(=Uu37;;kamrL_|%PxIiGR5#P3Nu&$ybNKUUH;T?VX~Jwew*=F1{=KKi(0WY=CX+5-+QipeKbb$5)3+R>=c}g=t;_V+^g^1~!IyM%1834@`&6En*Jo=e&u>QNll=p4+OL`}lpo>W^S-e~dfnXc2VRHyj#u<?q^C>x{+~bja*g<?gXFTQLaz(M*6@Ae{<21Vp*V``Q>tp{(xJvR>Za*(U74@H(fTyKuH<as^|^0TUSr-f#iUz&M&{O-xA6+@xAAUvjdf*<{CQ4kURFcT7|82f+N7w)yesDOeILD)o+~-<R5;n&FC$$j*+tKl6gnn?`h`_|zjuCI$oE||>GHW!%2RBXM&FCFaL!>`e@h>J-W*Efc+~9(#R>hM*R7o^Klj~6ldep0B3+4G#@`bT<DxvR>~rC^$0=G*|9Skmh+R&3DU*(pE|?nfzVmo~?x*)oBz<fuujiAV+5EW*N}}}}o?lDZ9@35Hfa&lR?jN$1@-&a?&)*-e|4gBN=N*)v+;;-q7vvFB&QPB2siaFKlll3y(=CJI-)qG4Z}B*p<{3SWbTP_{#}UWU`6)WvC^W7tjm{5Y!lzVE(@a~^%>irq`}t@)dXCJ$%_Ci?@aOA&_*^0TK9@}D$E@e?&%fW}`@y9T*X>Z>xxP7+f9O)ug?VYbKAQ&6dd)c*q?_{kQXRw&E<B%B11Vq2(g~E0(laKV#{148-Q?g!y0oM{-ABxW_K_~wuBLq>cKaLMkIda0(Y~(rUW0CYubHZL^7A!*BEOI1B~X5f%M~6cbuq11nK+T^FMsobpHBla`1w99o5$@MK<hTXm(7b;<ml@!{^8E=3AQn$iysB^eLQwRGOa%(pZgo`1DbBU56BLov|lVYSMWTye!=s(l192|iA?n|KikXm+4PL-GoJD1u#W@n8}lcx_&wElZwXn+?|=5C{CgZ0M*H8gFrVv&dy%Fa??vX@ov41sdzWQE7}qy^O6RjOa?CNkZoI!)ggc}Q(kXuLI2l2C${w%y`za)r-wXFFr~NDh4B_iG+#4;kvq+cr`}6zJA5Q$dk3Gll5r+GxIb|a4cj>_zeqSANhtFGCM7kLElHW7Z=hA)?{=7q|%<M=0vimMNw=MgFXrCJI&!#_ONmsVS^SX9#%kSy&;|ZnnO(-98zu&puFr$Rm<12p8Z`XnEgS05VUq;M|qj8Nq=pLx)a&z~S6sKfQoHbp3chFI5x)K?hua9rO)gyuIyXKtCu%b&}o1?7h@{BII*5Zg;ey<T<zSu3%YM#(*<q2K+Xm_r)IL7?NgEmRl>Z9q(z@79xNDUVAbIRNPgx+7%m8#9LG|!76@mBRVKSx^ArS#ba`uJKMl$4@`3@f_)p(Vnau8et^Z7q)Fpi`k<m&<P^S<ACpH{_}5ra~phS{!5kvNA2jT75KKtEar>0I%oAE%`o9&*ab9<>$OUcHX@1_Cxt|kkN+D731H(^42l@o+93f*3YZyV(b<EcgPmM1grYX=)-!wdf$%oNwlUb^G_YJrkf6Q&-S#Uiw}M+)a#P(pUKwpsn!koXu3)GAjfK)jn4~e=+3{TTC0PmSJ%IMGU>|MBm8%Uw%18Fy|Urw(MdaA_mWb&f0*Oy@$<AQH%cF0)3xV9+qXtt+qartUFS!S60PY<uRUgKx-jZtmZue6cI#K9*Q@uNAs<aQ=2PvD=g6pQ&yl8^3O1x!tAnO%byg~-^12y*|1n3-<ocMg<Sz%0qI-_iCgr@f{jBN6{aj1O{?T;fem3gbem3gbem3gbe%5s3ey*h(@-gn`TK?G2)w*Fn8+EPDChr`cr{Q-wvD4@a`hBRy(RAavT}#J#sOiS@*{Ey#s+K?Yl~LFBm8Kid=UTcUALIFK)V1@uS~r}}M!mY8>l69C-*A7>bmRTOsB7<KO*h^XjJkGDsO67)f>GD*3Dxr&?g>WSn2+(EP)o->LDP-*1fx!M^Q!Udc39hqgXK5WkZNlnG!y)MbU$q~k$p6@{?qpC9{<%(+udEd{l7nL&sTGps<y?zY2c&O)>myKfc?Ok&p7xo91p%kZPV4Z0QedB0`OVDPjuWHeTHLod?fk|Ki2UN(Puau+)Hf(VIK$^<D=C!0QLc}c_Funn13SX)3_J<UWmbXyxOwW76D8EUk}?lU<CN*u&n~F178Im3|s>q3?2Yn2_67G6F5)DW%L;?(($$EGhC|UU!c!$Ie56*4#R#JwzXJa7VKHDg=6jKVLuOB0&?Dfyfz?@l~`j0>=CeOzTxl-$DA^J5@1h&jq%B9^HtlY;6CUxoT9ebz!~7oXA<m_U}JoR+5*+K5I6^%p$Rcfn8z1Bez5z&HV5<gV=jh4;0#wI=4#Bh5I)ObUj|!{ZVhvRv%$5T<^p}ewK?Vj7lPMSTOGC42ik%+fUP00J~;aqwZEvXCGbt~mf-IK|ElA!qtEai9dC?2!)7|(2z`c4!0psl5B7SnHAcQRu-m|9hqVZ>3$WQD=hu+eYslkGtgSxm^<mR|?cisJIbVm5E$p_iG5)^VdZ?`<uqSvc*hFAQ@Hb$y2a4eK;BNun1Ahy=1+YDM3-H!JM;-5mK0_BBcSoP0hmH?HpW#q&SGDzry+3U3Sf2#D1e+_??g_gmY(0^)6Y_FG9__Klj<9!xP4jhypDX6<2A`g=_k@k{kJL6;ZM}hR;KN|+1MCex6gCfFA8-$F7vKlrF5r&94&aX9t$_|Y-VS|+Z|itl^cgnQ@iyo)Yy$4Awob5jf~_sq*9-PuusLJxgJ2&7n;UZOioCiaj}BO4Z`gaorujO<&lz*JgO3~RZm==lU2R>|)>+{1_AzRkptdNr9amd2@HF^lwQW<|Uf@CS3bkETTP5&E@MMh52c8Ari?LC_<KX%5sQ_Np#lDHS41We^F%|eSECpvV4<RnYIPkOZxeB}qejGlhfeJWV<95W`j#ygkF!(Y&0nTC;BQC>h;BoL#fM>v2%n-y2L99a<a}DcccpqHB*ivAzZq5SuGQ0%N=8A?d!xV5f*A~pja3A<JjJ*%M1AYc$i-85;VHkS?7!A&1Zi2>eH#m!V5pfy*0M242Auhu_@O>B?4g4Ow06v$17r~?9lLAZvXZ8!2kKt`_W<P}(40FKQTsski;SumW_*?{D0RJ97Nx)O!Z0#EnZzE#u#@JkpXIKu-#zta1!$fd4_DhUsxC{IO#@+^6z)xXp4loydC&nHDM(XB_f-l2la5mRw_%hrJ&gQDXd<-kW6EQXym=C@SV<Ul4;JNTA2UdU|Ra=bOQi18<Th;cB+V%s#1;4De>uS3T{0Tf2V+(;L;QKN5C@==R5I&cI*LAUPAuhuQ;4Ee)d>NL3vzXr@F2j@HCGfcpyagTupLAd*I9uZm#M^;bT5L0X8ODOMnCB3e;SKPU@W}*bfU}sPh!=`j-(k!Rtdn6CcqYb{0nh2?EP^k?E8uLdWAJ5|2F~XC8uKwc0Dc2wtAO{wGcfiXun63Yv9Z8o;4J1>&=~Fk_ZnWurkU-3`mbsK{>XG8)&EB|<H(wS_UlL9Qe##B2;eom9=m(07g`&-#P4NqZ{c5UghMm'

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
