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

PART_NAME = 'part_002'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/358eb80d4d074dee8cd65b4b0fa187f7/part_002.stl', 'relative_path': '358eb80d4d074dee8cd65b4b0fa187f7/part_002.stl', 'source_sha256': 'f91f2824e4787ac705bd1b7f255491b173bd4a8b08c972b625ce214eb0362f5b', 'input_faces': 456, 'input_vertices': 378, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.24304604530334473, -0.3215293288230896, -0.461904913187027], [0.2066744565963745, 0.17452019453048706, 0.33508723974227905]]}
GEOMETRY_BASE85 = 'c$}r133L_J8OJ9<1QF3-6hzR66ax|>0%1`k4-_S=QA`9x@?uCx07FP1fEFFG+NxNqAl>T&%hHM!By3g5a{(h|lSSFoSFKC6D&hiKtG##TcONs~OwZ|QbI$*Ke}4CyJNLWyd-DcPC>Y-4luXP0>1e(GPD87soh(bMrIl&bmDS9wEG?_esj8lvW}W45{bS<7QH3K5#-&+x*6mr7%4$n%vM!Hg4JhxIl^w|{pI$SwrlhKPdd;LV&95n$R$HccZAD3Snfh~=UVZyzM|yS5j?9bvk3TK+8ZK(Tt3k(2-InC3U@u&{t|5d+7kpM9#_j1{)`an7t7)slc%t}&6=6I+ebus1KC=3kq4RIQV{sU_>K~jJ$_LJ?@$n8_9uKV-9;nyk%X;B~df|b34VU#AF6)I`J4C&P%X$r$_2vwzcjlM%!eg>tlP~LqN6r-W8Xgn%8eT2xg~vyUdf`b~FWlN7>NR|jzg~N9lXYSB8g7evQ~9D^!)3jOM@7A<d{M9AvR=bwy@p#G{q?5!U{UYW7bYCONYo3D%X;BSSuZ>$>oxPpdJUKL!tK$bUU*`ssMoCj8Bwp{L;Uqdv+U4%4VU$%@~i#z8ZPTKJR#~$%`fUraZ#_~Nl|ZVJ)+(e7xg9<y}rfiH&L(QNl~xi5mB$<aZzt7zr<f}iqG)ZYq(wDuh;OzE`Pm-TMhntQ#@bv^OHqe!|F9$)@!(|*Kk>HDqqx_;-X%|Wxa;WdJUKLra1N5m7nf##>Mxq<mUS*kk98=a`Sy8x%obl+<gBAINwKs`T72p+<YGe_&`yw`2LkVkT1T!Bsb50!{zf|a`XI5aq;{N@FD(u`TPlRkuN{LlFNRO{V#b^^n>hw$xZ(U@=N^vAp2i()Blp2{+HbJe}GeOqQzd{xtl(h-1NERrq3leeIDTSd4SXBlAHIg0H@DWT)am~o{;Mo?@<9B6YCf6QIebY3dxgl{o*~!aQR*&xm>?|FOobe)-T_SB$w-#??sZE_o5UR?>Uku<@&{YPGBCne(|0oxp~i#+`Q*VZoc;om+vi-oA(yU<@)7&OJIJne)--ac~Y!jzPA`I-$Nvii1o|&kU)NkfBo`3L~`?7lH5F(Bu{-WKQ^Y(;SIgq=WN}>JH6bV{kF62$bcs9-#6;N-Kt}3amN>QjK90=h>tJ0E#bt*Hyv)bzr&ZG_^Rj)FSp5$AAHE+@s=aDgssPLxt`eM7SD&}8!qz`d8?fJB|cra&zbkC@Al?-c;rKu+i%U-@8#C~VuwdQI^fUGbb0KKKD)i#o^^)96B#wWd7@KY9^L#e-#oF04(!!2c_P<8Poc|W-48nXak0)A>x_&0+UCB8hr0VavE04ys)M_{Jl69qXMU^4A&1A__*;X+U%KAOx3)aj=;et=T^?QE`z0?=j^6IBv+HJGzLnwf$P>Ms{N(W!o1MJPW$yle`gWt2Tf^M-#K*kjaO;C*&xZAn;j(}1{j);z4VU@R;oY7MtJiQ@ui>&@!)3kE^LIVt{Q3KsTkldokKXHYYY_9m;~9tC`Iq^5a?e3`{w#Mr_UNB(3hRHvW&cMiTWkvJbHiny8!r1f#YKN6EBy1D{xn?nXS^Z0(a9fI>gIpdeXp0t_8oCQ7u7D0t!TY5?DK25{5%>iKX--)K6fLQZV3Inz-8YWF8el>FFs$18C4FqAGzDz=SPq3@$zJUmnW9LxX;UDU%Gv0KVxtA^2lQPbK{{#U;espo%=>R`saxhxjb>9|Go*^?OQ8ymv8<=N0-~}4?FY6lY7=Xb-wDJm-X0&?Oq;R=AM_`X`?$&cIBF|{x@9qzu~g~4VV2N+udwUSpORy=>PlPcmEzdV2r!Zf9&M;Gdy`FpWlyNZa=i%;qv)lxO_esE}svE%jZMl$+fG)`rmNb|H(aft`6IO!{z=bw^pnU>o>z?zZow3&2ZUoseI9IseI9IhRc3SanWzF@7lThwu|+g5!>zM_INixk>~Q{(Pd9L`*UQDo4@4-ACJA}^5}-YH+p%b;+T8i<No|)iOb{Xf9U4FabTr0kNAEuJn(%~wQ)sQzTq<8I(5S1Vf|*f>^H+@zZow3Eq-9plCb?TT<(wIa(@h$`xDK%dP&&lE5*e*8ZOV#aQS((9#3Bq_IWov@P0V|k?#kF<QpEyKmOkRc_HUzc;NjZfBmAce8Xja<mg%Mze9=j7#?`vKHh3gSia$b_uC_t^<nEVJh1)=eb<MsA0Ft>!H;YTT@PHY$BwmpJ}lqx!1H<UrWeB2W4K&T?8vL3`GyD9A0NFXbp7za{{Nz|F>HRr1M|ZJ^P7A*f1~@HvyPqP^h;!EkNPkkd;ZXhFrIkj+2vu}YJ2b}K5iGf{diBbK9r}8_vfE>VtHsjJTBJ*x3-D(n0eC0{A;sUhRzQU%nuLDZ|0HnfA_<uo&AyX!|f&_|E~*NF83dvl<R><<$BCK?b!d?Cth)QpVJ<8)>AaUK8)M7!|(O+Rjn2}=l*rmbz$6^m^0tU@BG}|XPIw!vB+=CT^X8hxX8Dk-s$eA$T!@MiTMk!U+cshMZNIIYwxTG<?Gij51psZ-Ji&}ncJK{w|vy;+xYV3^<msP*5w{Ax8F^7=1Gct!>upK|M`e*Vdo{ez29AbfUk4cAK;vCii`7=+?;QUi}MZeVv#S-H^4={JYUJp`KIO(=PS86-vD1P_D7trHF~DY<?~SR)bmjA)bmjA)br4A`8<@|JP!?*&qKlEay{~SDCbER^ULR<;DPz&^H9zs=a<hz!Bfve!{zf(@T6Rid>+bq^z*R5_uE1{Zyx$`@*Fjl(rH$vRbJxxRUr-akBQ;GDpc9~zxq|7-no7L-(MAaT&-b+(lX*7@XPSe5nsVShi@SM9p8X&lIF&<(_F8meN*B&_@?+aO5K&ZDqV`S??%kRcf)rkcEoqacOqVh?}YC_JP+Rie?GAdz76ZqeyLjj?{#k??Uxgu#V^ONByPs9#5WSt(_G((|A2T3UQ7GduygUP@tI0FN|z{QBkj8oe}M0TznFLt{$hND*d8CjUqEb!zX0Esn2FD1J=*J@(R;Ln7{}+ZzDtSS@t>-(kCi?l{sZ4!jh(7=8nGGv6LR#pj(V&)^XM^?)13Tgl>f8RI$}NkfYR%hJN`Oj+8<PUjq%qQJHR#djMp=EkZaa?at`7*DQ!^NNL-J9K`Ej1BJp|rMsi*tCh(gWd(m^f_Ae{Fq_mZ|1^=GXyGrj9|Aya6&U?gn@h>y>zUO-F|ElzcQj&NC|4*gkj2~xA`)`!KV*D${{>e2*7(c?;H(ZnS<a~oqQ)l+QrHvcE!=IsadYU_aI%C?mRBFL^3&yn9*XV0o5?hd)mUePJ3#R?Q)E~c9`iS@;{wy_iCgVElG3_&yZ<Xebw<1UTkGNKk>!`;vxZce75#!pwrTihKH;ISwUn_lKx#M3jru_+}FB$)mv9G!2Fyn_AJHa(?dU8(S-%)y7=~d!x{O3x?7(d3C_Ma&oW&9{(pL5M_#&<LJ8P~k($@vVwTIorpHN;i;{YrZo-^-ZxJCy#y_+J>?&o!$UU&YuCu36*B*@1sb>5oc(B0hoNr?iLhJ&b9;U1=NR+Zfx&n7Qsx<Y~WF>1m~1#GUx-)fwNQG=^A+@2k{DX&Sl}cDd3ON;6P3Y=F|0O0}p4)?cZgQWcsG8>BRwxn?t$_C1v<xTb<@v>(WQs?khXf9A|3PQ~|S&6g1;;|H*|!NfWE9*j>$<*>ozTt%FVk8=N+s1Bz0thdq>G|j_$FmE|yn)Onur0z;;?g`JOo~ev!mZvm}y`IHhUkSg8_0450k2Te?-*xP@_7hl}S?74zO!jvoiouGx*DO>5o65f5jBbLBrIt!G4pz?o-iV4|rL3(E-2$7-zE47BusYTiL$|=DQHNQ7wWrQ<?pH*;Q&{6z&w3_%);*PaZesnF>_M@o-szrwnaldh*q>R{RO(s(9GG6i)vQCuYw-GB*K$7{hu}w1;|O95ukUpo_tSACK1Tf`koLp4&rt3)9zTIN3_pzg3EX=Kdo&hr_G$=q455Z1)_*f=zZRd*x`wm15_~Z+AD>TtF?CI%rt9zp?89jG;1+x-u>fB{eko_8&!~o2m3H!TU&C3<#?K&D;dS5W{<)Pn13!Zt^IXxff>?#GR?pTsO6Q={EtmaF=@&{@qF%6{D0Nk`i5KFlxpoGzC4R2bx!mJi?lFgX?o+x1b%o7VYOQo9u|59BN*60VMC^foOzG!Jm!qp;kKunuyb6D>QfKDt%v?Waj>Ss-(dDq2N@ps~BA$h>Q947Zme>kkr<6e*8PuTtZAxvpt_|1Jkbj5L`6vVSL#6Y$|9RY7`(G<Xm3~Fc!~argAZIp^Gt>UJN`sYtLmY(H`421gMgw7wD)r;Keq8fg?z>Q_4~oKU%k6=?h!Omcl=T19xrg`z{5++0)Yp#Mw7*@cE&J4#J<@)@rT@BbS$7jJ!t0)B&)&6X@3hxFr+aTM@m%~Y&TbyD9ln;cyPen;f4@>U?%$1jYyVTFOD(sLbnJ{@pwykZyHm6F4=80bUp8}T|A<m9dz#ChE@Xb)*FDgsFnw0~^VbXYhAmR+%enRC%(Q<{DTj6Cu%-pvSNBUE%7y9AhW?B!Cichc`E|bxLVaO(an|<{FTvl#SwBe3!Qai<JwVLH>mU7psS1$x<B6I0@%RbE3-A;06Nz2$6Y(*na-~U1*C6c&5O2W`!1pA^@G<7;$+g!qUpam<aVUN=zJi#KufSIlhv6&nQ<SDFRVj@|+K(dMiXVj^Nt}isi623niXVX=PMm_D!hMHxuOZxjI=+l}1-=YlO1unTiZ3B%;Y;wvO5>Dnvh+XFxzhe@;?4N8@g0c8_+sYiz_rbpZybIsu^E0W{zl@d_#5#>#HRQne4*v`-gVZ=AMMkK*W=Uh>BKSkbbJ%y4frPbQ;3E5LhgGC^|hzQ4*0W)tv&nG+OvnPsk=G888HLj46kd|{i~lBJ(2bUh*w%C`(JzW8PWb)r2SChK>Sd=?q%IWx|gCz`#fSkKA-$NVsGo@^GEw!r2QqtUe?KX1MRyKyWn-a0ADaXEj_czfBLVaCx2{xfWH4&DzEhav$FTf9Q80u{UdY1@TPii)xoDbUpV>tZNd6CSaJl#'

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
